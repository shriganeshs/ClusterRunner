import tempfile
from test.framework.functional.base_functional_test_case import BaseFunctionalTestCase
from test.functional.job_configs import JOB_WITH_SETUP_AND_TEARDOWN

from genty import genty, genty_dataset, genty_repeat


@genty
class TestShutdown(BaseFunctionalTestCase):

    @genty_dataset(
        should_wait_for_process_exit=(True,),
        should_not_wait_for_process_exit=(False,)
    )
    @genty_repeat(10)
    def test_shutdown_all_slaves_should_kill_all_slaves(self, should_wait_for_process_exit):
        master = self.cluster.start_master()
        self.cluster.start_slaves(2)

        master.graceful_shutdown_all_slaves()

        slaves_response = master.get_slaves()
        slaves = slaves_response['slaves']
        living_slaves = [slave for slave in slaves if slave['is_alive']]
        dead_slaves = [slave for slave in slaves if not slave['is_alive']]

        self.assertEqual(0, len(living_slaves))
        self.assertEqual(2, len(dead_slaves))

        if should_wait_for_process_exit:
            print('Waiting for slaves to die')
            self.assertTrue(self.cluster.block_until_slaves_dead(10))


    # def test_shutdown_one_slave_should_leave_one_slave_alive(self):
    #     master = self.cluster.start_master()
    #     self.cluster.start_slaves(2)
    #
    #     master.graceful_shutdown_slaves_by_id([1])
    #
    #     slaves_response = master.get_slaves()
    #     slaves = slaves_response['slaves']
    #     living_slaves = [slave for slave in slaves if slave['is_alive']]
    #     dead_slaves = [slave for slave in slaves if not slave['is_alive']]
    #
    #     self.assertEqual(1, len(living_slaves))
    #     self.assertEqual(1, len(dead_slaves))
    #
    # def test_shutdown_all_slaves_while_build_is_running_should_finish_build_then_kill_slaves(self):
    #     master = self.cluster.start_master()
    #     self.cluster.start_slaves(2)
    #
    #     project_dir = tempfile.TemporaryDirectory()
    #     build_resp = master.post_new_build({
    #         'type': 'directory',
    #         'config': JOB_WITH_SETUP_AND_TEARDOWN.config,
    #         'project_directory': project_dir.name,
    #         })
    #     build_id = build_resp['build_id']
    #
    #     master.block_until_build_started(build_id, timeout=10)
    #
    #     # Shutdown one on the slaves and test if the build can still complete
    #     master.graceful_shutdown_slaves_by_id([1])
    #
    #     master.block_until_build_finished(build_id, timeout=30)
    #
    #     self.assert_build_has_successful_status(build_id=build_id)
    #
    #     slaves_response = master.get_slaves()
    #     slaves = slaves_response['slaves']
    #     living_slaves = [slave for slave in slaves if slave['is_alive']]
    #     dead_slaves = [slave for slave in slaves if not slave['is_alive']]
    #
    #     self.assertEqual(1, len(living_slaves))
    #     self.assertEqual(1, len(dead_slaves))

