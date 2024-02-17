from __future__ import annotations

import hashlib
import json
import re
from typing import Optional, Dict

from seeq.sdk import *
from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._redaction import safely
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.workbooks._item_map import ItemMap


class Item:
    """
    The base class of all objects in the spy.workbooks module that represent
    items in Seeq. Each item is described by the dictionary stored at its
    `dictionary` property.
    """

    _definition: dict
    _datasource: Optional[DatasourcePreviewV1]
    _provenance: str

    available_types = dict()

    CONSTRUCTOR = 'CONSTRUCTOR'
    PULL = 'PULL'
    LOAD = 'LOAD'
    TEMPLATE = 'TEMPLATE'
    ROOT = '<root>'

    def __init__(self, definition=None, *, provenance=None):
        if isinstance(definition, Item):
            definition = definition.definition_dict

        _common.validate_argument_types([(definition, 'definition', dict)])

        self._definition = definition if definition else dict()
        self._datasource = None

        if 'ID' not in self._definition:
            self._definition['ID'] = _common.new_placeholder_guid()

        if 'Type' not in self._definition:
            self._definition['Type'] = self.__class__.__name__

            # Reduce the derived classes down to their base class
            if self._definition['Type'] in ['Analysis', 'Topic']:
                self._definition['Type'] = 'Workbook'
            if 'Worksheet' in self._definition['Type']:
                self._definition['Type'] = 'Worksheet'
            if 'Workstep' in self._definition['Type']:
                self._definition['Type'] = 'Workstep'

        self._provenance = Item.CONSTRUCTOR if provenance is None else provenance

    def __contains__(self, key):
        return _common.present(self._definition, key)

    def __getitem__(self, key):
        return _common.get(self._definition, key)

    def __setitem__(self, key, val):
        self._definition.__setitem__(key, _common.ensure_upper_case_id(key, val))

    def __delitem__(self, key):
        self._definition.__delitem__(key)

    def __repr__(self):
        return '%s "%s" (%s)' % (self.type, self.fqn, self.id)

    # The following properties/functions (definition, get) exist for backward compatibility for a time when
    # code directly accessed the definition object.
    @property
    def definition(self):
        return self

    @definition.setter
    def definition(self, val):
        self._definition = val

    def get(self, key, value=None):
        return self[key] if key in self else value

    @property
    def fqn(self):
        """
        The "fully qualified name" (FQN) of this item, which includes the Path and Asset (if present).
        For example: "Example >> Cooling Tower 1 >> Area A >> Temperature"
        :return: The fully qualified name of this item.
        """
        return _common.fqn_from_row(self.definition)

    @property
    def id(self):
        return _common.get(self.definition, 'ID')

    @property
    def name(self):
        return _common.get(self.definition, 'Name')

    @name.setter
    def name(self, value):
        self.definition['Name'] = value

    @property
    def type(self):
        return _common.get(self.definition, 'Type')

    @property
    def datasource(self) -> DatasourcePreviewV1:
        return self._datasource

    @property
    def definition_hash(self):
        return self.digest_hash(self.definition_dict)

    @property
    def definition_dict(self):
        return self._definition

    @property
    def provenance(self):
        return self._provenance

    @staticmethod
    def digest_hash(d):
        # We can't use Python's built-in hash() method as it produces non-deterministic hash values due to using a
        # random seed
        hashed = hashlib.md5()
        hash_string = str(json.dumps(d, sort_keys=True, skipkeys=True))
        hashed.update(hash_string.encode('utf-8'))
        return hashed.hexdigest()

    def refresh_from(self, new_item, item_map: ItemMap, status: Status):
        self._definition = new_item.definition_dict
        self._provenance = new_item.provenance

    def _construct_data_id(self, label):
        return '[%s] %s' % (label, self.id)

    def find_me(self, session: Session, label, datasource_output):
        # This is arguably the trickiest part of the spy.workbooks codebase: identifier management. This function is
        # a key piece to understanding how it works.
        #
        # When we push items to a server, we are trying our best not to create duplicates when the user doesn't
        # intend to. In other words, operations should be idempotent whenever it is expected that they should be.
        #
        # First, we look up an item by its identifier in case our in-memory object actually corresponds directly to
        # an existing item. This will happen whenever items are constructed by virtue of executing spy.workbooks.pull(),
        # or if the user does a spy.workbooks.push() without specifying refresh=False.
        #
        # If that method doesn't work, then we try to look up the item using a canonical Data ID format,
        # which incorporates the ID field from the in-memory object, which may have been generated (in the case where
        # self.provenance equals Item.CONSTRUCTOR) or may come from a different system (in the case where
        # self.provenance equals Item.PULL or Item.Load).
        #
        # If that doesn't work and the item was created by just constructing it in memory (i.e. self.provenance
        # equals Item.CONSTRUCTOR), then the item types will try to look it up by name.
        #
        # A label can be used to purposefully isolate or duplicate items. If a label is specified, then we never look
        # up an item directly by its ID, we fall through to the canonical Data ID format (which incorporates the
        # label). This allows many copies of a workbook to be created, for example during training scenarios.

        items_api = ItemsApi(session.client)

        if not label:
            try:
                item_output = items_api.get_item_and_all_properties(id=self.id)  # type: ItemOutputV1
                return item_output
            except ApiException:
                # Fall through to looking via Data ID
                pass

        data_id = self._construct_data_id(label)
        _filters = [
            'Datasource Class==%s && Datasource ID==%s && Data ID==%s' % (
                datasource_output.datasource_class, datasource_output.datasource_id, data_id),
            '@includeUnsearchable']

        search_results = items_api.search_items(
            filters=_filters,
            offset=0,
            limit=2)  # type: ItemSearchPreviewPaginatedListV1

        if len(search_results.items) == 0:
            return None

        if len(search_results.items) > 1:
            raise SPyRuntimeError('Multiple workbook/worksheet/workstep items found with Data ID of "%s"', data_id)

        return search_results.items[0]

    @staticmethod
    def _get_item_output(session: Session, item_id: str) -> ItemOutputV1:
        items_api = ItemsApi(session.client)
        return items_api.get_item_and_all_properties(id=item_id)

    @staticmethod
    def _dict_from_item_output(item_output: ItemOutputV1):
        def _parse(val):
            if val == 'true':
                return True
            elif val == 'false':
                return False
            else:
                return val

        definition = {prop.name: _parse(prop.value) for prop in item_output.properties}
        definition['Name'] = item_output.name
        definition['Type'] = item_output.type

        if 'UIConfig' in definition:
            try:
                definition['UIConfig'] = json.loads(definition['UIConfig'])
            except ValueError:  # ValueError includes JSONDecodeError
                pass

        # For some reason, these are coming back as lower case, which makes things inconsistent
        if 'Scoped To' in definition and isinstance(definition['Scoped To'], str):
            definition['Scoped To'] = definition['Scoped To'].upper()

        return definition

    @staticmethod
    def _dict_via_attribute_map(item, attribute_map):
        d = dict()
        for attr, prop in attribute_map.items():
            if hasattr(item, attr):
                d[prop] = getattr(item, attr)

        return d

    @staticmethod
    def _property_input_from_scalar_str(scalar_str):
        match = re.fullmatch(r'([+\-\d.]+)(.*)', scalar_str)
        if not match:
            return None

        uom = match.group(2) if match.group(2) else None
        return PropertyInputV1(unit_of_measure=uom, value=float(match.group(1)))

    @staticmethod
    def formula_string_from_list(formula_list):
        return '\n'.join(formula_list) if isinstance(formula_list, list) else str(formula_list)

    @staticmethod
    def formula_list_from_string(formula_string):
        return formula_string.split('\n') if '\n' in formula_string else formula_string

    @staticmethod
    def _get_derived_class(_type):
        if _type not in Item.available_types:
            raise SPyTypeError('Type "%s" not supported in this version of seeq module' % _type)

        return Item.available_types[_type]

    @staticmethod
    def pull(item_id, *, allowed_types=None, session: Session = None, status: Optional[Status] = None):
        session = Session.validate(session)
        item_output = safely(lambda: Item._get_item_output(session, item_id),
                             action_description=f'pull Item {item_id}', status=status)
        if item_output is None:
            return None
        definition = Item._dict_from_item_output(item_output)
        if allowed_types and definition['Type'] not in allowed_types:
            return None

        derived_class = Item._get_derived_class(definition['Type'])
        item = derived_class(definition, provenance=Item.PULL)  # type: Item
        item._pull(session, item_id, status)
        item._datasource = item_output.datasource
        return item

    @staticmethod
    def from_dict(definition, *, provenance=PULL):
        derived_class = Item._get_derived_class(definition['Type'])
        item = derived_class(definition, provenance=provenance)  # type: Item
        return item

    def _pull(self, session: Session, item_id: str, status: Status):
        pass

    @staticmethod
    def load(definition):
        derived_class = Item._get_derived_class(definition['Type'])
        item = derived_class(definition, provenance=Item.LOAD)
        return item

    def _set_formula_based_item_properties(self, calculated_item):
        self._definition['Formula'] = Item.formula_list_from_string(self._definition['Formula'])
        self._definition['Formula Parameters'] = dict()
        for parameter in calculated_item.parameters:  # type: FormulaParameterOutputV1
            if parameter.item:
                self._definition['Formula Parameters'][parameter.name] = parameter.item.id
            else:
                self._definition['Formula Parameters'][parameter.name] = parameter.formula

    def _scrape_auth_datasources(self, session: Session) -> Dict[str, DatasourceOutputV1]:
        return dict()


class Reference:
    JOURNAL = 'Journal'
    DETAILS = 'Details'
    SCOPED = 'Scoped'
    DEPENDENCY = 'Dependency'
    EMBEDDED_CONTENT = 'Embedded Content'
    DATE_RANGE_CONDITION = 'Date Range Condition'
    ASSET_SELECTION = 'Asset Selection'

    def __init__(self, _id, _provenance, worksheet=None):
        """
        :type _id: str
        :type _provenance: str
        :type worksheet: Worksheet
        """
        self.id = _id
        self.provenance = _provenance
        self.worksheet = worksheet

    def __repr__(self):
        if self.worksheet is not None:
            return '%s reference on "%s" (%s)' % (self.provenance, self.worksheet.name, self.id)
        else:
            return '%s (%s)' % (self.provenance, self.id)


def replace_items(document, item_map: ItemMap):
    if document is None:
        return

    new_report = document
    for _id in item_map.keys():
        matches = re.finditer(_id, document, flags=re.IGNORECASE)
        for match in matches:
            _replacement = item_map[_id]
            try:
                new_report = re.sub(re.escape(match.group(0)), _replacement, new_report, flags=re.IGNORECASE)
            except (TypeError, IndexError):
                pass

    return new_report


def get_canonical_server_url(session: Session):
    url = session.client.host.replace('/api', '').lower()  # type: str
    if url.startswith('http:') and url.endswith(':80'):
        url = url.replace(':80', '')
    if url.startswith('https:') and url.endswith(':443'):
        url = url.replace(':443', '')

    return url


class ItemList(list):

    def _index_of(self, key) -> Optional[int]:
        if isinstance(key, str):
            candidates = list()
            for i in range(len(self)):
                item: Item = super().__getitem__(i)
                if key == item.id:
                    candidates.append((i, item))
                elif key == item.name:
                    candidates.append((i, item))
                elif key == item.fqn:
                    candidates.append((i, item))

            if len(candidates) == 0:
                return None
            elif len(candidates) > 1:
                error_str = '\n'.join([f'{i}: {item}' for i, item in candidates])
                raise IndexError(f'"{key}" matches multiple items in list:\n{error_str}')
            else:
                return candidates[0][0]

        return key

    def __contains__(self, key):
        return self._index_of(key) is not None

    def __getitem__(self, key) -> Item:
        index = self._index_of(key)
        if index is None:
            raise IndexError(f'"{key}" not found in list')

        return super().__getitem__(index)

    def __setitem__(self, key, val: Item):
        index = self._index_of(key)
        return super().__setitem__(index, val)

    def __delitem__(self, key):
        index = self._index_of(key)
        return super().__delitem__(index)
