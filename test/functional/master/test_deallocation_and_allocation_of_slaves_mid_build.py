import tempfile
import yaml
import os

from test.framework.functional.base_functional_test_case import BaseFunctionalTestCase
from test.functional.job_configs import JOB_WITH_SLEEPS


class TestDeallocationAndAllocationOfSlavesMidBuild(BaseFunctionalTestCase):
    def test_build_completes_after_allocating_deallocatin_and_reallocating_slaves_to_build(self):
        master = self.cluster.start_master()
        # Only one slave, with one executor. This means that the slave should be able to
        # theoretically finish the build in 5 seconds, as this job definition has 5 atoms,
        # with each sleeping for 1 second.
        self.cluster.start_slaves(1, num_executors_per_slave=1)
        project_dir = tempfile.TemporaryDirectory()
        build_resp = master.post_new_build({
            'type': 'directory',
            'config': yaml.safe_load(JOB_WITH_SLEEPS.config[os.name])['BasicSleepingJob'],
            'project_directory': project_dir.name,
        })
        build_id = build_resp['build_id']
        master.block_until_build_started(build_id, timeout=10)
        master.graceful_shutdown_all_slaves()
        self.cluster.block_until_n_slaves_dead(num_slaves=1, timeout=10)
        self.cluster.start_slaves(1, num_executors_per_slave=1)
        master.block_until_build_finished(build_id, timeout=10)
        self.assert_build_has_successful_status(build_id)
