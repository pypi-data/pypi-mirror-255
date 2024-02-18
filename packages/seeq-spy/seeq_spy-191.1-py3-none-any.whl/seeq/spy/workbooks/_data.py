from __future__ import annotations

import json
import os
import re
import textwrap
from typing import List, Dict, Union, Optional

import pandas as pd

from seeq import spy
from seeq.base import util
from seeq.sdk import *
from seeq.spy import _common, _compatibility, _metadata
from seeq.spy._errors import *
from seeq.spy._redaction import safely
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy._workbook_context import WorkbookContext
from seeq.spy.workbooks._item import Item, ItemMap


class StoredOrCalculatedItem(Item):
    def __init__(self, definition=None, *, provenance=None):
        super().__init__(definition, provenance=provenance)

        self.scoped_to = None

    def _populate_asset_and_path(self, session: Session, item_id, status):
        trees_api = TreesApi(session.client)
        asset_tree_output = safely(
            lambda: trees_api.get_tree(id=item_id),
            action_description=f'get Tree information for {item_id}',
            status=status)  # type: AssetTreeOutputV1
        if asset_tree_output is None or asset_tree_output.item is None:
            return

        ancestors = [a.name for a in asset_tree_output.item.ancestors]

        _common.add_ancestors_to_definition(self.type, self.name, ancestors, self.definition, old_asset_format=False)

        if len(asset_tree_output.item.ancestors) > 0:
            self.definition['Parent ID'] = asset_tree_output.item.ancestors[-1].id

    def _pull(self, session: Session, item_id, status):
        super()._pull(session, item_id, status)

        if 'Path' not in self.definition:
            self._populate_asset_and_path(session, item_id, status)

    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        raise SPyRuntimeError('Pushed called but StoredOrCalculatedItem.push() not overloaded')

    def _attach_to_parent(self, session: Session, item_map: ItemMap, item_id: str):
        if self['Scoped To'] is None:
            # Do not move around global items
            return

        if 'Parent ID' not in self.definition:
            return

        parent_id = self.definition['Parent ID']
        if parent_id != Item.ROOT and self.definition['Parent ID'] not in item_map:
            return

        trees_api = TreesApi(session.client)
        if parent_id == Item.ROOT:
            trees_api.move_nodes_to_root_of_tree(body=ItemIdListInputV1(items=[item_id]))
        else:
            trees_api.move_nodes_to_parent(parent_id=item_map[self.definition['Parent ID']],
                                           body=ItemIdListInputV1(items=[item_id]))

    @staticmethod
    def _find_datasource_name(datasource_class, datasource_id, datasource_maps):
        for datasource_map in datasource_maps:
            if datasource_map['Datasource Class'] == datasource_class and \
                    datasource_map['Datasource ID'] == datasource_id:
                return datasource_map['Datasource Name']

        raise SPyRuntimeError('Could not find Datasource Class "%s" and Datasource ID "%s" in datasource maps' %
                              (datasource_class, datasource_id))

    def _execute_regex_map(self, old_definition, regex_map, regex_map_index, item_map: ItemMap, *,
                           allow_missing_properties=False):
        capture_groups = dict()
        for prop, regex in regex_map['Old'].items():
            if prop not in StoredItem.SEARCHABLE_PROPS:
                searchable_props_string = '\n'.join(StoredItem.SEARCHABLE_PROPS)
                raise SPyRuntimeError(
                    f'Datasource Map contains an unsearchable property "{prop}".'
                    f'Searchable properties:\n{searchable_props_string}')

            if prop not in old_definition:
                if allow_missing_properties:
                    continue
                else:
                    item_map.log(self.id, f'- RegEx-Based Map {regex_map_index}: Unsuccessful match. Details:')
                    item_map.log(self.id, f'    "{prop}" not defined for this item')
                    return None, None

            pythonized_regex = util.pythonize_regex_capture_group_names(regex)
            match = re.fullmatch(pythonized_regex, old_definition[prop])
            if not match:
                item_map.log(self.id, f'- RegEx-Based Map {regex_map_index}: Unsuccessful match. Details:')
                item_map.log(self.id, f'    "{prop}"')
                item_map.log(self.id, f'        regex          "{regex}"')
                item_map.log(self.id, f'        does not match "{old_definition[prop]}"')
                return None, None

            capture_groups.update(match.groupdict())

        new_definition = dict()
        for prop, regex in regex_map['New'].items():
            new_definition[prop] = util.replace_tokens_in_regex(regex, capture_groups, escape=False)

        return new_definition, capture_groups

    def _lookup_item_via_datasource_map(
            self, session: Session, pushed_workbook_id: str, datasource_maps: List[Dict],
            item_map: ItemMap, *, only_override_maps: bool = False) -> Optional[Item]:
        item: Optional[Item] = None

        item_map.clear_logs(self.id)

        # First, we process the "overrides". These are the cases where, even if the item with the ID exists in the
        # destination, we still want to map to something else. Useful for swapping datasources on the same server.
        overrides = [m for m in datasource_maps if _common.get(m, 'Override', default=False)]
        if len(overrides) > 0:
            if "File" in overrides[0]:
                item_map.log(self.id, f'Using overrides from {os.path.dirname(overrides[0]["File"])}:')
            item = self._lookup_in_datasource_map(session, pushed_workbook_id, overrides, item_map)
        else:
            item_map.log(self.id, f'No datasource map overrides found')

        if item is not None:
            item_map.log(self.id, f'Successful mapping:')
            item_map.log(self.id, f'  Old: {self}')
            item_map.log(self.id, f'  New: {item}')
            return item

        if only_override_maps:
            item_map.log(self.id, f'{self} not mapped, only override maps used', at_top=True)
            return None

        # Second, we just try to look the item up by its ID. This case will occur when the user pulls a workbook,
        # makes a change, and pushes it back.
        try:
            item = Item.pull(self.id, session=session)
        except ApiException:
            item_map.log(self.id, f"Item's ID {self.id} not found directly in target server")

        if item is not None:
            item_map.log(self.id, f"Item's ID {self.id} found directly in target server")
            return item

        # Finally, we try to use the non-override maps to find the item. This case will occur mostly when
        # transferring workbooks between servers.
        non_overrides = [m for m in datasource_maps if not _common.get(m, 'Override', default=False)]
        if len(non_overrides) > 0:
            if "File" in non_overrides[0]:
                item_map.log(self.id, f'Using non-overrides from {os.path.dirname(non_overrides[0]["File"])}:')
            item = self._lookup_in_datasource_map(session, pushed_workbook_id, non_overrides, item_map)
        else:
            item_map.log(self.id, f'No (non-override) datasource maps found')

        if item is None:
            item_map.log(self.id, f'{self} not successfully mapped', at_top=True)
            return None

        item_map.log(self.id, f'Successful mapping:')
        item_map.log(self.id, f'  Old: {self}')
        item_map.log(self.id, f'  New: {item}')

        return item

    def _lookup_in_datasource_map(self, session: Session, pushed_workbook_id, datasource_maps,
                                  item_map: ItemMap) -> Optional[Item]:
        item: Optional[Item] = None

        relevant_maps = list()
        for datasource_map in datasource_maps:
            if _common.get(self, 'Datasource Class') != _common.get(datasource_map, 'Datasource Class') or \
                    _common.get(self, 'Datasource ID') != _common.get(datasource_map, 'Datasource ID'):
                continue

            relevant_maps.append(datasource_map)
            if "File" in datasource_map:
                item_map.log(self.id, f'- Used "{datasource_map["File"]}"')
            else:
                item_map.log(self.id,
                             f'- Used datasource map for Datasource Class "{datasource_map["Datasource Class"]}" '
                             f'and Datasource ID "{datasource_map["Datasource ID"]}"')

            if _common.DATASOURCE_MAP_ITEM_LEVEL_MAP_FILES in datasource_map:
                item = self._lookup_in_item_level_map_files(session, datasource_map, item_map)

            if item is not None:
                break

            if _common.DATASOURCE_MAP_REGEX_BASED_MAPS in datasource_map:
                item = self._lookup_in_regex_based_map(session, datasource_map, datasource_maps, item_map,
                                                       pushed_workbook_id)

            if item is not None:
                break

        if len(relevant_maps) == 0:
            item_map.log(
                self.id,
                f'- No Datasource Maps found that match Datasource Class "{_common.get(self, "Datasource Class")}" '
                f'and Datasource ID "{_common.get(self, "Datasource ID")}"')

        return item

    def _lookup_in_item_level_map_files(self, session: Session, datasource_map,
                                        item_map: ItemMap) -> Optional[Item]:
        item: Optional[ItemOutputV1] = None
        item_level_map_files = datasource_map['Item-Level Map Files']
        if not isinstance(item_level_map_files, list):
            item_level_map_files = [item_level_map_files]

        if 'DataFrames' not in datasource_map:
            datasource_map['DataFrames'] = dict()

        df_map = datasource_map['DataFrames']

        for item_level_map_file in item_level_map_files:
            if item_level_map_file not in df_map:
                if not util.safe_exists(item_level_map_file):
                    raise SPyValueError('Item-Level Map File "%s" does not exist' % item_level_map_file)

                df_map[item_level_map_file] = pd.read_csv(item_level_map_file)

            df = df_map[item_level_map_file]

            if 'Old ID' not in df.columns or 'New ID' not in df.columns:
                raise SPyValueError('Item-Level Map File must have "Old ID" and "New ID" columns')

            mapped_row = df[df['Old ID'] == self.id]

            if len(mapped_row) > 1:
                raise SPyValueError('Ambiguous map: %d rows in "%s" match "Old ID" == "%s"\n%s' % (
                    len(mapped_row), item_level_map_file, self.id, mapped_row))

            if len(mapped_row) == 0:
                item_map.log(
                    self.id,
                    f'- Item-Level Map File "{item_level_map_file}" did not match for "Old ID" value "{self.id}"')
                continue

            new_id = mapped_row.iloc[0]['New ID']

            item = Item.pull(new_id, session=session)
            break

        return item

    def _lookup_in_regex_based_map(
            self, session: Session, datasource_map, datasource_maps, item_map: ItemMap,
            pushed_workbook_id) -> Optional[Union[ItemOutputV1, UserOutputV1, IdentityPreviewV1]]:
        items_api = ItemsApi(session.client)

        item: Optional[Item] = None
        new_definition = None
        regex_map_index = None
        regex_map = None
        capture_groups = None
        for i in range(len(datasource_map['RegEx-Based Maps'])):
            regex_map_index = i
            regex_map = datasource_map['RegEx-Based Maps'][regex_map_index]
            old_definition = self.definition_dict

            if 'Type' not in old_definition:
                raise SPyValueError('"Type" property required in "Old" datasource map definitions')

            if 'Datasource Class' in old_definition and 'Datasource ID' in old_definition:
                old_definition['Datasource Name'] = \
                    StoredOrCalculatedItem._find_datasource_name(old_definition['Datasource Class'],
                                                                 old_definition['Datasource ID'],
                                                                 datasource_maps)

            new_definition, capture_groups = self._execute_regex_map(
                old_definition, regex_map, regex_map_index, item_map,
                allow_missing_properties=self.type.endswith('Datasource'))

            if new_definition is not None:
                break

        if new_definition is None:
            return None

        if 'Type' not in new_definition:
            raise SPyValueError('"Type" property required in "New" datasource map definitions')

        if 'Datasource Name' in new_definition:
            if 'Datasource ID' not in new_definition:
                if 'Datasource Class' not in new_definition:
                    raise SPyValueError('"Datasource Class" required with "Datasource Name" in map:\n%s' %
                                        json.dumps(new_definition))

                datasource_results = items_api.search_items(
                    # Note here that 'Name' supports RegEx but 'Datasource Class' doesn't. Users have to be careful in
                    # the Datasource Maps not to supply a RegEx. See Workbook._construct_default_datasource_maps().
                    filters=['Datasource Class==%s&&Name==/%s/' % (new_definition['Datasource Class'],
                                                                   new_definition['Datasource Name']),
                             '@includeUnsearchable'],
                    types=['Datasource'],
                    limit=2)  # type: ItemSearchPreviewPaginatedListV1

                items = datasource_results.items
                if len(items) > 1:
                    # Try filtering out any archived items first
                    items = [i for i in items if not i.is_archived]

                if len(items) > 1:
                    multiple_items_str = "\n".join([i.id for i in items])
                    raise SPyRuntimeError(
                        f'Multiple datasources found that match "{new_definition["Datasource Name"]}":\n'
                        f'{multiple_items_str}'
                    )
                elif len(items) == 0:
                    item_map.log(self.id, f'- No datasource found that matches "{new_definition["Datasource Name"]}"')
                    return None

                new_datasource = items[0]  # type: ItemSearchPreviewV1
                try:
                    new_definition['Datasource ID'] = items_api.get_property(
                        id=new_datasource.id, property_name='Datasource ID').value
                except ApiException:
                    raise SPyRuntimeError(f'Could not get Datasource ID for '
                                          f'"{new_definition["Datasource Name"]}" {new_datasource.id}')

            del new_definition['Datasource Name']

        # Simplify the types so that the search will find stored or calculated signals/conditions etc. This
        # helps when mapping, for example, an AF tree to a Data Lab tree.
        for t in ['Signal', 'Condition', 'Scalar', 'Datasource']:
            if t in new_definition['Type']:
                new_definition['Type'] = t

        if new_definition['Type'] not in ['User', 'UserGroup']:
            query_df = pd.DataFrame([new_definition])
            from seeq.spy import _search
            if 'Path' in new_definition:
                # If we're matching based on path, unfortunately we will not be able to match against archived items
                # due to a limitation of the API. See CRAB-18439.
                search_df = _search.search(query_df, workbook=pushed_workbook_id, recursive=False,
                                           ignore_unindexed_properties=False, session=session, quiet=True)
            else:
                search_df = _search.search(query_df, workbook=pushed_workbook_id, include_archived=True,
                                           ignore_unindexed_properties=False, session=session, quiet=True)

            # If several things are returned, but some of them are archived, then filter out the archived ones.
            # Tested by spy.workbooks.tests.test_push.test_datasource_map_by_name()
            if len(search_df) > 1 and 'Archived' in search_df.columns:
                search_df = search_df[~search_df['Archived']]

            def _log_criteria(_and_found=None):
                for key, value in new_definition.items():
                    item_map.log(self.id, f'    "{key}"')
                    if key in regex_map['Old']:
                        item_map.log(self.id, f'        regex          "{regex_map["Old"][key]}"')
                        item_map.log(self.id, f'        matched on     "{self[key]}"')
                    item_map.log(self.id, f'        searched for   "{value}"')
                    if _and_found is not None:
                        item_map.log(self.id, f'        and found      "{_and_found[key]}"')
                if capture_groups is not None and len(capture_groups) > 0:
                    item_map.log(self.id, f'    Capture groups:')
                    for n, v in capture_groups.items():
                        item_map.log(self.id, f'        {n:14} "{v}"')

            if len(search_df) == 0:
                item_map.log(self.id, f'- RegEx-Based Map {regex_map_index}: Item not found on server. Details:')
                _log_criteria()
            elif len(search_df) > 1:
                item_map.log(self.id, f'- RegEx-Based Map {regex_map_index}: Multiple matches for item found. Details:')
                _log_criteria()
                item_map.log(self.id, f'  Matching items:')
                item_map.log(self.id, textwrap.indent(f'{str(search_df[["ID", "Name"]])}', '    '))
            else:
                item = Item.pull(search_df.iloc[0]['ID'], session=session)
                item_map.log(self.id, f'- RegEx-Based Map {regex_map_index}: Successfully matched. Details:')
                _log_criteria(item)
        else:
            if new_definition['Type'] == 'User':
                try:
                    users_api = UsersApi(session.client)
                    user = users_api.get_user_from_username(
                        auth_datasource_class=new_definition['Datasource Class'],
                        auth_datasource_id=new_definition['Datasource ID'],
                        username=new_definition['Username'])  # type: UserOutputV1
                    from seeq.spy.workbooks._user import User
                    item = User.pull(user.id, session=session)
                except ApiException:
                    # Fall through, item not found
                    pass
            else:
                user_groups_api = UserGroupsApi(session.client)
                user_groups = user_groups_api.get_user_groups()
                for user_group in user_groups.items:  # type: IdentityPreviewV1
                    if user_group.name == new_definition['Name']:
                        from seeq.spy.workbooks._user import UserGroup
                        item = UserGroup.pull(user_group.id, session=session)
                        break

        return item


class StoredItem(StoredOrCalculatedItem):
    SEARCHABLE_PROPS = ['Datasource Class', 'Datasource ID', 'Datasource Name', 'Data ID',
                        'Type', 'Name', 'Description', 'Username', 'Path', 'Asset']

    def _push_dummy_item(self, session: Session, datasource_output, item_map: ItemMap, workbook_context):
        definition_dict = self.definition_dict.copy()

        definition_dict['Original ID'] = definition_dict['ID']
        definition_dict['Original Datasource Class'] = definition_dict['Datasource Class']
        definition_dict['Original Datasource ID'] = definition_dict['Datasource ID']
        definition_dict['Original Data ID'] = definition_dict['Data ID']
        del definition_dict['ID']
        del definition_dict['Datasource Class']
        del definition_dict['Datasource ID']

        # Dummy items will be pushed with a Path and Asset so that it gets put in a (minimal) tree and therefore can
        # be asset-swapped.

        item = StoredItem._push_it(session, definition_dict, workbook_context, datasource_output, item_map)

        item_map.log(self.id, f'Dummy item pushed: {item}')

        return item

    def _push_local_item(self, session: Session, pushed_workbook_id, label, datasource_output, item_map: ItemMap):
        definition_dict = self.definition_dict.copy()

        workbook_context = WorkbookContext(spy.workbooks.Analysis({'ID': pushed_workbook_id}), None)

        if ('ID' in definition_dict
                and (label is not None
                     or 'Scoped To' in definition_dict and definition_dict['Scoped To'] != pushed_workbook_id)):
            # If we're pushing with a label or if the item being pushed does not belong to this workbook,
            # then we don't want to push the existing item.
            del definition_dict['ID']

        # Change the Data ID to use the pushed workbook's ID so it's properly differentiated
        definition_dict['Data ID'] = definition_dict['Data ID'].replace(self['Scoped To'], pushed_workbook_id)

        # Scope it to the pushed workbook
        definition_dict['Scoped To'] = pushed_workbook_id

        # For local items, the whole tree should be coming in via the item inventory and so we'll hook it up to those
        # assets later (via Parent ID).
        if 'Parent ID' in definition_dict:
            for key in ['Path', 'Asset']:
                if key in definition_dict:
                    del definition_dict[key]

        item = StoredItem._push_it(session, definition_dict, workbook_context, datasource_output, item_map)

        self._attach_to_parent(session, item_map, item.id)

        item_map.log(self.id, f'Local item pushed: {item}')

        return item

    @staticmethod
    def _push_it(session: Session, definition_dict, workbook_context: WorkbookContext, datasource_output,
                 item_map: ItemMap):
        push_results_df = _metadata.push(session, pd.DataFrame([definition_dict]), workbook_context, datasource_output,
                                         Status(quiet=True, errors='raise'))
        push_results_df.drop(columns=['Push Result'], inplace=True)
        item = Item.from_dict(push_results_df.iloc[0].to_dict())

        # We add it as a dummy item here so that spy.workbooks.job.data.push() can populate it with data. This is
        # useful for data imported via CSV or SPy.
        item_map.add_dummy_item(push_results_df)

        return item

    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        if self.id in item_map.data_item_cache:
            return item_map.data_item_cache[self.id]

        local: bool = self['Scoped To'] is not None
        only_override_maps = item_map.only_override_maps
        if local and label is not None:
            only_override_maps = True

        item = self._lookup_item_via_datasource_map(session, pushed_workbook_id, datasource_maps, item_map,
                                                    only_override_maps=only_override_maps)
        if item is None:
            if local:
                if ('Parent ID' in self.definition and
                        self.definition['Parent ID'] != Item.ROOT and self.definition['Parent ID'] not in item_map):
                    raise SPyDependencyNotFound(f'Parent ID {self.definition["Parent ID"]} of {self.id} not found')
                item = self._push_local_item(session, pushed_workbook_id, label, datasource_output, item_map)
            else:
                if dummy_items_workbook_context is None:
                    raise SPyDependencyNotFound(item_map.explain(self.id))
                item = self._push_dummy_item(session, datasource_output, item_map, dummy_items_workbook_context)
        else:
            if local:
                item_scope = _common.get(item, 'Scoped To')
                item_is_scoped_to_other_workbook = item_scope is not None and item_scope != pushed_workbook_id
                self_already_exists_and_may_need_update = (
                        item_scope is not None
                        and item_scope == pushed_workbook_id
                        and _common.get(self, 'ID') == _common.get(item, 'ID')
                        and not label
                )
                if item_is_scoped_to_other_workbook or self_already_exists_and_may_need_update:
                    item = self._push_local_item(session, pushed_workbook_id, label, datasource_output, item_map)

        item_map[self.id] = item.id
        item_map.data_item_cache[self.id] = item

        if item.type not in ['User', 'UserGroup']:
            # We need to exclude Example Data, because it is set explicitly by the connector
            datasource_class = item['Datasource Class']
            datasource_id = item['Datasource ID']
            is_example_data = (datasource_class and datasource_class == 'Time Series CSV Files' and
                               datasource_id and datasource_id == 'Example Data')

            if override_max_interp and item.type == 'StoredSignal' and not is_example_data and \
                    'Maximum Interpolation' in self:
                src_max_interp = Item._property_input_from_scalar_str(self['Maximum Interpolation'])
                dst_max_interp_prop = item['Maximum Interpolation']
                if dst_max_interp_prop:
                    dst_max_interp = Item._property_input_from_scalar_str(dst_max_interp_prop.value)
                    if src_max_interp.unit_of_measure != dst_max_interp.unit_of_measure or \
                            src_max_interp.value != dst_max_interp.value:
                        items_api = ItemsApi(session.client)
                        items_api.set_property(id=item.id,
                                               property_name='Override Maximum Interpolation',
                                               body=src_max_interp)

        return item


class Asset(StoredItem):
    def __init__(self, definition=None, *, provenance=None):
        super().__init__(definition, provenance=provenance)

        if self.provenance == Item.LOAD:
            if self.definition.get('Old Asset Format', True):
                if self.type == 'Asset':
                    if self.definition.get('Path') in [None, '']:
                        self.definition['Path'] = self.definition['Asset']
                    else:
                        self.definition['Path'] += ' >> ' + self.definition['Asset']
                        self.definition['Asset'] = self.definition['Name']

        self.definition['Old Asset Format'] = False


class Datasource(StoredItem):
    @staticmethod
    def from_datasource_output(datasource_output: Union[DatasourceOutputV1, DatasourcePreviewV1]):
        return Datasource({
            'ID': datasource_output.id,
            'Name': datasource_output.name,
            'Datasource Class': datasource_output.datasource_class,
            'Datasource ID': datasource_output.datasource_id,
            'Archived': datasource_output.is_archived
        })


class CalculatedItem(StoredOrCalculatedItem):
    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        if self.id in item_map.data_item_cache:
            return item_map.data_item_cache[self.id]

        # This is a key piece of datasource mapping logic. CalculatedItems that are in trees are more like "source
        # data" in the context of workbooks/worksheets. In other words, when we push them, we want to map in existing
        # items rather than creating a standalone CalculatedItem that isn't a part of a tree, has no associated asset
        # and cannot be swapped.
        is_standalone_item = _common.get(self, 'Asset') is None

        # So if it's in a global tree, we process the datasource maps just like we would if it were a StoredItem. If
        # it's *not* in a global tree, then we only process datasource maps that have been supplied in a
        # datasource_map_folder and are therefore treated as "overrides". CalculatedItems that are associated with the
        # particular analysis of a workbook should be created/overwritten as part of the push, and since they won't
        # exist in a tree, we purposefully don't attempt to do any mapping and we fall through to the CalculatedItem's
        # create/update code.
        local: bool = self['Scoped To'] is not None
        only_override_maps = item_map.only_override_maps
        if (local and label is not None) or is_standalone_item:
            only_override_maps = True

        item = self._lookup_item_via_datasource_map(
            session, pushed_workbook_id, datasource_maps, item_map, only_override_maps=only_override_maps)

        if not local and not is_standalone_item and item is None:
            raise SPyDependencyNotFound(item_map.explain(self.id))

        if (local and 'Parent ID' in self.definition and
                self.definition['Parent ID'] != Item.ROOT and self.definition['Parent ID'] not in item_map):
            raise SPyDependencyNotFound(f'Parent ID {self.definition["Parent ID"]} of {self.id} not found')

        if item:
            item_map[self.id] = item.id
            item_map.data_item_cache[self.id] = item

        return item

    def _find(self, session: Session, label, datasource_output, pushed_workbook_id):
        item_output = self.find_me(session, label, datasource_output)

        if item_output is None and self.provenance == Item.CONSTRUCTOR:
            item_output = self._find_by_name(session, pushed_workbook_id)

        return item_output

    def _find_by_name(self, session: Session, workbook_id):
        items_api = ItemsApi(session.client)

        _filters = ['Name==%s' % self.name,
                    '@includeUnsearchable']

        search_results = items_api.search_items(
            filters=_filters,
            scope=[workbook_id],
            types=[self.type],
            offset=0,
            limit=1)  # type: ItemSearchPreviewPaginatedListV1

        if len(search_results.items) == 0:
            return None

        return search_results.items[0]

    def _create_calculated_item_input(self, clazz, item_map: ItemMap, scoped_to, scope_globals_to_workbook):
        item_input = clazz()
        item_input.name = self.definition['Name']
        if 'Description' in self.definition:
            item_input.description = self.definition['Description']
        item_input.formula = Item.formula_string_from_list(self.definition['Formula'])

        parameters = list()
        if 'Formula Parameters' in self.definition:
            for parameter_name, parameter_id in self.definition['Formula Parameters'].items():
                if parameter_id not in item_map:
                    raise SPyDependencyNotFound(f'{self} formula parameter {parameter_name}={parameter_id} not found')

                parameters.append('%s=%s' % (parameter_name, item_map[parameter_id]))

        for _attr_name in ['formula_parameters', 'parameters']:
            if hasattr(item_input, _attr_name):
                setattr(item_input, _attr_name, parameters)

        if 'Number Format' in self.definition:
            item_input.number_format = self.definition['Number Format']

        if scope_globals_to_workbook or _common.present(self.definition, 'Scoped To'):
            item_input.scoped_to = scoped_to

        return item_input

    def _set_ui_config(self, session: Session, _id):
        if 'UIConfig' in self.definition:
            try:
                items_api = ItemsApi(session.client)
                items_api.set_property(id=_id, property_name='UIConfig',
                                       body=PropertyInputV1(value=json.dumps(self.definition['UIConfig'])))
            except ValueError:  # ValueError includes JSONDecodeError, but ApiException will not be caught
                pass


class StoredSignal(StoredItem):
    pass


class CalculatedSignal(CalculatedItem):
    def _pull(self, session: Session, item_id, status):
        super()._pull(session, item_id, status)
        # Note: The caller of this function is in charge of API safety
        signals_api = SignalsApi(session.client)
        signal_output = signals_api.get_signal(id=item_id)  # type: SignalOutputV1
        self._set_formula_based_item_properties(signal_output)

    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        session = Session.validate(session)
        # Note: The caller of this function is in charge of API safety
        item = super().push(session, datasource_maps, datasource_output, pushed_workbook_id=pushed_workbook_id,
                            item_map=item_map, label=label, override_max_interp=override_max_interp,
                            scope_globals_to_workbook=scope_globals_to_workbook)

        if item:
            return item

        signals_api = SignalsApi(session.client)

        item_output = self._find(session, label, datasource_output, pushed_workbook_id)

        signal_input = self._create_calculated_item_input(SignalInputV1, item_map,
                                                          pushed_workbook_id,
                                                          scope_globals_to_workbook)  # type: SignalInputV1

        if item_output is None:
            signal_output = signals_api.put_signal_by_data_id(datasource_class=datasource_output.datasource_class,
                                                              datasource_id=datasource_output.datasource_id,
                                                              data_id=self._construct_data_id(label),
                                                              body=signal_input)  # type: SignalOutputV1
        else:
            signal_output = signals_api.put_signal(id=item_output.id,
                                                   body=signal_input)  # type: SignalOutputV1

        self._set_ui_config(session, signal_output.id)

        item_map[self.id] = signal_output.id

        self._attach_to_parent(session, item_map, signal_output.id)

        return signal_output


class StoredCondition(StoredItem):
    pass


class CalculatedCondition(CalculatedItem):
    def _pull(self, session: Session, item_id, status):
        super()._pull(session, item_id, status)
        # Note: The caller of this function is in charge of API safety
        conditions_api = ConditionsApi(session.client)
        condition_output = conditions_api.get_condition(id=item_id)  # type: ConditionOutputV1
        self._set_formula_based_item_properties(condition_output)

    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        # Note: The caller of this function is in charge of API safety
        item = super().push(session, datasource_maps, datasource_output, pushed_workbook_id=pushed_workbook_id,
                            item_map=item_map, label=label, override_max_interp=override_max_interp,
                            scope_globals_to_workbook=scope_globals_to_workbook)

        if item:
            return item

        conditions_api = ConditionsApi(session.client)

        item_output = self._find(session, label, datasource_output, pushed_workbook_id)

        condition_update_input = self._create_calculated_item_input(
            ConditionUpdateInputV1, item_map,
            pushed_workbook_id, scope_globals_to_workbook)  # type: ConditionUpdateInputV1
        condition_update_input.replace_capsule_properties = True

        if item_output is None:
            condition_update_input.datasource_class = datasource_output.datasource_class
            condition_update_input.datasource_id = datasource_output.datasource_id
            condition_update_input.data_id = self._construct_data_id(label)
        else:
            # There is no easy way to update a Condition by its ID, so we have to retrieve its data id triplet
            condition_output = conditions_api.get_condition(id=item_output.id)  # type: ConditionOutputV1
            condition_update_input.datasource_class = condition_output.datasource_class
            condition_update_input.datasource_id = condition_output.datasource_id
            condition_update_input.data_id = condition_output.data_id

        item_batch_output = conditions_api.put_conditions(
            body=ConditionBatchInputV1(conditions=[condition_update_input]))  # type: ItemBatchOutputV1

        item_update_output = item_batch_output.item_updates[0]  # type: ItemUpdateOutputV1
        if item_update_output.error_message is not None:
            raise SPyRuntimeError('Could not push condition "%s": %s' %
                                  (self.definition['Name'], item_update_output.error_message))

        self._set_ui_config(session, item_update_output.item.id)

        item_map[self.id] = item_update_output.item.id

        self._attach_to_parent(session, item_map, item_update_output.item.id)

        return item_update_output.item


class LiteralScalar(StoredItem):
    pass


class CalculatedScalar(CalculatedItem):
    def _pull(self, session: Session, item_id, status):
        super()._pull(session, item_id, status)
        # Note: The caller of this function is in charge of API safety
        scalars_api = ScalarsApi(session.client)
        calculated_item_output = scalars_api.get_scalar(id=item_id)  # type: CalculatedItemOutputV1
        self._set_formula_based_item_properties(calculated_item_output)

    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        # Note: The caller of this function is in charge of API safety
        item = super().push(session, datasource_maps, datasource_output, pushed_workbook_id=pushed_workbook_id,
                            item_map=item_map, label=label, override_max_interp=override_max_interp,
                            scope_globals_to_workbook=scope_globals_to_workbook)

        if item:
            return item

        scalars_api = ScalarsApi(session.client)
        items_api = ItemsApi(session.client)

        item_output = self._find(session, label, datasource_output, pushed_workbook_id)

        scalar_input = self._create_calculated_item_input(
            ScalarInputV1, item_map,
            pushed_workbook_id, scope_globals_to_workbook)  # type: ScalarInputV1

        if item_output is None:
            datasource_class = datasource_output.datasource_class
            datasource_id = datasource_output.datasource_id
            scalar_input.data_id = self._construct_data_id(label)

            if _compatibility.is_force_calculated_scalars_available():
                body = PutScalarsInputV1(datasource_class=datasource_class,
                                         datasource_id=datasource_id,
                                         scalars=[scalar_input],
                                         force_calculated_scalars=True)
            else:
                body = PutScalarsInputV1(datasource_class=datasource_class,
                                         datasource_id=datasource_id,
                                         scalars=[scalar_input])

            item_batch_output = scalars_api.put_scalars(body=body)  # type: ItemBatchOutputV1

            item_update_output = item_batch_output.item_updates[0]  # type: ItemUpdateOutputV1
            if item_update_output.error_message is not None:
                raise SPyRuntimeError('Could not push scalar "%s": %s' %
                                      (self.definition['Name'], item_update_output.error_message))

            self._set_ui_config(session, item_update_output.item.id)
            item_map[self.id] = item_update_output.item.id

            self._attach_to_parent(session, item_map, item_update_output.item.id)

            return item_update_output.item

        else:
            # There is no easy way to update a Scalar by its ID, so we have to use ItemsApi
            items_api.set_formula(id=item_output.id, body=FormulaUpdateInputV1(formula=scalar_input.formula,
                                                                               parameters=scalar_input.parameters))
            if scalar_input.scoped_to:
                items_api.set_scope(id=item_output.id, workbook_id=scalar_input.scoped_to)
            else:
                items_api.set_scope(id=item_output.id)
            props = [ScalarPropertyV1(name='Name', value=scalar_input.name)]
            if 'Definition' in self:
                props.append(ScalarPropertyV1(name='Description', value=scalar_input.description))
            if 'Number Format' in self:
                props.append(ScalarPropertyV1(name='Number Format', value=scalar_input.number_format))
            items_api.set_properties(id=item_output.id, body=props)
            self._set_ui_config(session, item_output.id)
            item_map[self.id] = item_output.id
            self._attach_to_parent(session, item_map, item_output.id)
            return item_output


class Chart(CalculatedItem):
    def _pull(self, session: Session, item_id, status):
        super()._pull(session, item_id, status)
        # Note: The caller of this function is in charge of API safety
        formulas_api = FormulasApi(session.client)
        calculated_item_output = formulas_api.get_function(id=item_id)  # type: CalculatedItemOutputV1

        self._set_formula_based_item_properties(calculated_item_output)

        if 'FormulaParameters' in self.definition:
            # Charts have these superfluous properties
            del self.definition['FormulaParameters']

    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        # Note: The caller of this function is in charge of API safety
        item = super().push(session, datasource_maps, datasource_output, pushed_workbook_id=pushed_workbook_id,
                            item_map=item_map, label=label, override_max_interp=override_max_interp,
                            scope_globals_to_workbook=scope_globals_to_workbook)

        if item:
            return item

        formulas_api = FormulasApi(session.client)
        items_api = ItemsApi(session.client)

        item_output = self._find(session, label, datasource_output, pushed_workbook_id)

        function_input = FunctionInputV1()
        function_input.name = self.definition['Name']
        function_input.type = self.definition['Type']
        function_input.formula = Item.formula_string_from_list(self.definition['Formula'])
        function_input.parameters = list()
        for parameter_name, parameter_id in self.definition['Formula Parameters'].items():
            if _common.is_guid(parameter_id):
                if parameter_id not in item_map:
                    raise SPyDependencyNotFound(
                        f'{self} formula parameter {parameter_name} ({parameter_id}) not pushed')

                function_input.parameters.append(FormulaParameterInputV1(name=parameter_name,
                                                                         id=item_map[parameter_id]))
            else:
                function_input.parameters.append(FormulaParameterInputV1(name=parameter_name,
                                                                         formula=parameter_id,
                                                                         unbound=True))

        if 'Description' in self.definition:
            function_input.description = self.definition['Description']

        function_input.scoped_to = pushed_workbook_id
        function_input.data_id = self._construct_data_id(label)

        if item_output is None:
            calculated_item_output = formulas_api.create_function(body=function_input)  # type: CalculatedItemOutputV1

            items_api.set_properties(
                id=calculated_item_output.id,
                body=[ScalarPropertyV1(name='Datasource Class', value=datasource_output.datasource_class),
                      ScalarPropertyV1(name='Datasource ID', value=datasource_output.datasource_id),
                      ScalarPropertyV1(name='Data ID', value=function_input.data_id)])
        else:
            calculated_item_output = formulas_api.update_function(id=item_output.id,
                                                                  body=function_input)  # type: CalculatedItemOutputV1

        self._set_ui_config(session, calculated_item_output.id)

        item_map[self.id] = calculated_item_output.id
        self._attach_to_parent(session, item_map, calculated_item_output.id)

        return calculated_item_output


class ThresholdMetric(CalculatedItem):
    def _pull(self, session: Session, item_id, status):
        super()._pull(session, item_id, status)
        # Note: The caller of this function is in charge of API safety
        formula_parameters = _metadata.formula_parameters_dict_from_threshold_metric(session, item_id)

        # These properties come through in the GET /items/{id} call, and for clarity's sake we remove them
        for ugly_duplicate_property in ['AggregationFunction', 'BoundingConditionMaximumDuration']:
            if ugly_duplicate_property in self.definition:
                del self.definition[ugly_duplicate_property]

        self.definition['Formula'] = '<ThresholdMetric>'
        self.definition['Formula Parameters'] = formula_parameters

    def push(self, session: Session, datasource_maps, datasource_output, *, pushed_workbook_id=None,
             item_map: ItemMap = None, label=None, override_max_interp=False, scope_globals_to_workbook=False,
             dummy_items_workbook_context=None):
        # Note: The caller of this function is in charge of API safety
        item = super().push(session, datasource_maps, datasource_output, pushed_workbook_id=pushed_workbook_id,
                            item_map=item_map, label=label, override_max_interp=override_max_interp,
                            scope_globals_to_workbook=scope_globals_to_workbook)

        if item:
            return item

        items_api = ItemsApi(session.client)
        metrics_api = MetricsApi(session.client)

        parameters = self['Formula Parameters']

        new_item = _metadata.threshold_metric_input_from_formula_parameters(parameters, item_object=self,
                                                                            item_map=item_map)

        new_item.name = self.name
        new_item.scoped_to = pushed_workbook_id
        new_item.number_format = _common.get(parameters, 'Number Format')

        item_output = self._find(session, label, datasource_output, pushed_workbook_id)

        while True:
            try:
                if item_output is None:
                    threshold_metric_output = metrics_api.create_threshold_metric(
                        body=new_item)  # type: ThresholdMetricOutputV1

                    items_api.set_properties(
                        id=threshold_metric_output.id,
                        body=[ScalarPropertyV1(name='Datasource Class', value=datasource_output.datasource_class),
                              ScalarPropertyV1(name='Datasource ID', value=datasource_output.datasource_id),
                              ScalarPropertyV1(name='Data ID', value=self._construct_data_id(label))])
                else:
                    threshold_metric_output = metrics_api.put_threshold_metric(
                        id=item_output.id,
                        body=new_item)  # type: ThresholdMetricOutputV1

                break

            except ApiException as e:
                # We have to handle a case where a condition on which a metric depends has been changed from bounded
                # to unbounded. In the UI, it automatically fills in the default of 40h when you edit such a metric,
                # so we do roughly the same thing here. This is tested by test_push.test_bad_metric().
                exception_text = _common.format_exception(e)
                if 'Maximum Capsule Duration for Bounding Condition must be provided' in exception_text:
                    new_item.bounding_condition_maximum_duration = '40h'
                else:
                    raise

        self._set_ui_config(session, threshold_metric_output.id)

        item_map[self.id] = threshold_metric_output.id
        self._attach_to_parent(session, item_map, threshold_metric_output.id)

        return threshold_metric_output
