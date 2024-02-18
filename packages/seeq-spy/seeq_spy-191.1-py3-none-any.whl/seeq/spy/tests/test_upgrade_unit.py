from unittest import mock

import pytest
from seeq import spy, sdk
from seeq.spy import Session
from seeq.spy._errors import SPyValueError


@pytest.mark.unit
def test_upgrade():
    mock_session = mock.Mock(Session)
    mock_session.client = {}
    mock_session.server_version = '999999.456.789'

    def _override_is_ipython():
        return True

    def _override_is_ipython_interactive():
        return True

    mock_kernel = mock.Mock()
    mock_ipython = mock.Mock()
    mock_ipython.kernel = mock_kernel

    def _override_get_ipython():
        return mock_ipython

    with mock.patch('seeq.spy._datalab.is_ipython', _override_is_ipython), \
            mock.patch('seeq.spy._datalab.is_ipython_interactive', _override_is_ipython_interactive), \
            mock.patch('IPython.get_ipython', _override_get_ipython):
        patched_variable = 'seeq.spy.__version__' if not hasattr(sdk, '__version__') else 'seeq.sdk.__version__'
        patched_version = '888888.0.0.100.10' if not hasattr(sdk, '__version__') else '888888.0.0'
        with mock.patch(patched_variable, patched_version):
            # Seeq Server version mismatch, so we'll install a compatible seeq module in addition to SPy
            spy.upgrade(session=mock_session)
            mock_ipython.run_cell.assert_called_with(
                f'pip install -U seeq~=999999.456 && pip install -U seeq-spy')
            assert not mock_kernel.do_shutdown.called

            # Upgrade can specify a particular SPy version.
            spy.upgrade(version='223.18', session=mock_session)
            mock_ipython.run_cell.assert_called_with(
                f'pip install -U seeq~=999999.456 && pip install -U seeq-spy==223.18')

        # Seeq Server version matches, so we'll only upgrade SPy
        patched_version = '999999.0.0.100.10' if not hasattr(sdk, '__version__') else '999999.0.0'
        with mock.patch(patched_variable, patched_version):
            spy.upgrade(session=mock_session)
            mock_ipython.run_cell.assert_called_with(f'pip install -U seeq-spy')

            # Upgrade can specify a particular SPy version.
            spy.upgrade(version='223.18', session=mock_session, force_restart=True)
            mock_ipython.run_cell.assert_called_with(f'pip install -U seeq-spy==223.18')
            mock_kernel.do_shutdown.assert_called_with(True)

            # Old server versioning scheme (before R50)
            mock_session.server_version = '0.456.789'
            with pytest.raises(SPyValueError, match='incompatible with Seeq Server version 0.456.789'):
                spy.upgrade(version='223.18', session=mock_session)

            spy.upgrade(session=mock_session)
            mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq-spy && pip install -U seeq~=0.456.789')

            # New server versioning scheme (R50 and after)
            mock_session.server_version = '50.456.789'
            with pytest.raises(SPyValueError, match='incompatible with Seeq Server version 50.456.789'):
                spy.upgrade(version='223.18', session=mock_session)

            spy.upgrade(session=mock_session)
            mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq-spy && pip install -U seeq~=50.456')

            # Going from R60+ SDK version to before R60 server version
            spy.upgrade(version='R50.0.1.184.15', session=mock_session)
            mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq-spy && pip install -U seeq==50.0.1.184.15')

            # Compatible module is found on PYTHONPATH
            with mock.patch('seeq.spy._login.find_compatible_module', lambda session: 'not None'):
                mock_session.server_version = '0.456.789'
                spy.upgrade(session=mock_session)
                mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq-spy && pip install -U seeq~=0.456.789')

                mock_session.server_version = '50.456.789'
                spy.upgrade(session=mock_session)
                mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq-spy && pip install -U seeq~=50.456')

                mock_session.server_version = '888888.456.789'
                spy.upgrade(session=mock_session)
                mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq && pip install -U seeq-spy')

        # Going from before R60 server version to R60+ SDK version
        patched_version = '58.0.0.100.10' if not hasattr(sdk, '__version__') else '58.0.0'
        with mock.patch(patched_variable, patched_version):
            mock_session.server_version = '999999.456.789'
            spy.upgrade(session=mock_session)
            mock_ipython.run_cell.assert_called_with(f'pip install -U seeq~=999999.456 && pip install -U seeq-spy')

            spy.upgrade(version='223.18', session=mock_session, force_restart=True)
            mock_ipython.run_cell.assert_called_with(
                f'pip install -U seeq~=999999.456 && pip install -U seeq-spy==223.18')
            mock_kernel.do_shutdown.assert_called_with(True)

            # Compatible module is found on PYTHONPATH
            with mock.patch('seeq.spy._login.find_compatible_module', lambda session: 'not None'):
                spy.upgrade(session=mock_session)
                mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq && pip install -U seeq-spy')

                spy.upgrade(version='283.12', session=mock_session)
                mock_ipython.run_cell.assert_called_with('pip uninstall -y seeq && pip install -U seeq-spy==283.12')

            mock_session.server_version = '58.456.789'
            spy.upgrade(session=mock_session)
            mock_ipython.run_cell.assert_called_with(f'pip install -U seeq~=58.456')

        with pytest.raises(SPyValueError, match='version argument "blah" is not a full version'):
            spy.upgrade(version='blah', session=mock_session)

    # Error expected if not in IPython
    with mock.patch('seeq.spy._datalab.is_ipython_interactive', _override_is_ipython_interactive), \
            mock.patch('IPython.get_ipython', _override_get_ipython):
        with pytest.raises(SPyValueError, match='must be invoked from a Jupyter notebook'):
            spy.upgrade(session=mock_session)

    # Error expected if not in a Jupyter notebook
    with mock.patch('seeq.spy._datalab.is_ipython', _override_is_ipython), \
            mock.patch('IPython.get_ipython', _override_get_ipython):
        with pytest.raises(SPyValueError, match='must be invoked from a Jupyter notebook'):
            spy.upgrade(session=mock_session)

    # Error expected if not able to get IPython instance
    with mock.patch('seeq.spy._datalab.is_ipython', _override_is_ipython), \
            mock.patch('seeq.spy._datalab.is_ipython_interactive', _override_is_ipython_interactive):
        with pytest.raises(SPyValueError, match='must be invoked from a Jupyter notebook'):
            spy.upgrade(session=mock_session)

    # Error expected if not able to get kernel for restart
    mock_ipython.kernel = None
    with mock.patch('seeq.spy._datalab.is_ipython', _override_is_ipython), \
            mock.patch('seeq.spy._datalab.is_ipython_interactive', _override_is_ipython_interactive), \
            mock.patch('IPython.get_ipython', _override_get_ipython):
        with pytest.raises(SPyValueError, match='Unable get IPython kernel to complete restart'):
            spy.upgrade(session=mock_session, force_restart=True)
