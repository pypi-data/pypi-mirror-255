#!/usr/bin/env python
import copy
import datetime
import io
import os
import subprocess
import tempfile
import unittest
import fsl_sub_plugin_slurm

from collections import defaultdict
from ruamel.yaml import YAML
from unittest.mock import patch

import fsl_sub.consts
from fsl_sub.exceptions import (
    BadSubmission,
    UnknownJobId
)
from fsl_sub.utils import (
    yaml_repr_none,
)

conf_dict = YAML(typ='safe').load('''---
method_opts:
    slurm:
        memory_in_gb: False
        queues: True
        copy_environment: False
        mail_support: True
        mail_modes:
            b:
                - BEGIN
            e:
                - END
            a:
                - FAIL
                - REQUEUE
            f:
                - ALL
            n:
                - NONE
        mail_mode: a
        set_time_limit: False
        array_holds: True
        array_limit: True
        preserve_modules: True
        add_module_paths: []
        keep_jobscript: False
copro_opts:
    cuda:
        resource: gpu
        classes: True
        class_resource: gputype
        class_types:
            K:
                resource: k80
                doc: Kepler. ECC, double- or single-precision workloads
                capability: 2
            P:
                resource: p100
                doc: >
                    Pascal. ECC, double-, single- and half-precision
                    workloads
                capability: 3
        default_class: K
        include_more_capable: True
        uses_modules: True
        module_parent: cuda
        no_binding: True
        class_constriant: True
queues:
    a.q:
''')
mconf_dict = conf_dict['method_opts']['slurm']


class TestSlurmUtils(unittest.TestCase):
    def test__sacct_datetimestamp(self):
        self.assertEqual(
            fsl_sub_plugin_slurm._sacct_datetimestamp('2018-06-04T10:30:30'),
            datetime.datetime(2018, 6, 4, 10, 30, 30)
        )

    def test__sacct_timstamp_seconds(self):
        self.assertEqual(
            fsl_sub_plugin_slurm._sacct_timestamp_seconds('10:10:10.10'),
            36610.1
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._sacct_timestamp_seconds('5-10:10:10.10'),
            468610.1
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._sacct_timestamp_seconds('1:10.10'),
            70.1
        )

    def test__day_time_minutes(self):
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('1-00:00:00'),
            24 * 60
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('1-00:01:00'),
            24 * 60 + 1
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('0-00:01:00'),
            1
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('0-00:00:01'),
            1
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('0-01:00:00'),
            60
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('0-01:01:00'),
            60 + 1
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('10:00'),
            10
        )
        self.assertEqual(
            fsl_sub_plugin_slurm._day_time_minutes('10'),
            1
        )

    def test__add_comment(self):
        comments = []
        comments.append('A comment')
        newcomments = list(comments)
        fsl_sub_plugin_slurm._add_comment(
            newcomments, 'A comment'
        )
        self.assertListEqual(
            comments,
            newcomments
        )
        fsl_sub_plugin_slurm._add_comment(
            newcomments, 'Another comment'
        )
        self.assertListEqual(
            ['A comment', 'Another comment', ],
            newcomments
        )

    def test__no_waiton(self):
        self.assertTrue(fsl_sub_plugin_slurm._no_waiton([]))
        self.assertTrue(fsl_sub_plugin_slurm._no_waiton(()))
        self.assertTrue(fsl_sub_plugin_slurm._no_waiton(None))
        self.assertTrue(fsl_sub_plugin_slurm._no_waiton(False))
        self.assertTrue(fsl_sub_plugin_slurm._no_waiton(''))

    def test__get_dependency(self):
        config = {'strict_dependancies': True, }
        self.assertEqual('afterok:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=1234))
        config = {'strict_dependancies': False, }
        self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=1234))
        config = {'strict_dependancies': False, }
        self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton="1234"))
        config = {'strict_dependancies': False, }
        self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=[1234, ]))
        config = {'strict_dependancies': False, }
        self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=["1234", ]))
        config = {'strict_dependancies': False, }
        self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=(1234, )))
        config = {}
        self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=1234))
        self.assertEqual(
            'afterany:1234?afternotok:1235',
            fsl_sub_plugin_slurm._get_dependency(config, waiton="afterany:1234?afternotok:1235"))
        with patch.dict(os.environ, {"FSLSUB_STRICTDEPS": "1"}, clear=True):
            self.assertEqual('afterok:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=1234))
        with patch.dict(os.environ, {"FSLSUB_STRICTDEPS": "0"}, clear=True):
            self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=1234))
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual('afterany:1234', fsl_sub_plugin_slurm._get_dependency(config, waiton=1234))
        config = {'array_holds': True, }
        self.assertEqual(
            'aftercorr:1234',
            fsl_sub_plugin_slurm._get_dependency(config, waiton=None, array_task=True, array_hold=1234))
        self.assertIsNone(
            fsl_sub_plugin_slurm._get_dependency(config, waiton=None, array_task=True))
        self.assertIsNone(fsl_sub_plugin_slurm._get_dependency(config, waiton=(), array_task=True))
        self.assertIsNone(fsl_sub_plugin_slurm._get_dependency(config, waiton=[], array_task=True))
        self.assertIsNone(fsl_sub_plugin_slurm._get_dependency(config, waiton=()))
        self.assertIsNone(fsl_sub_plugin_slurm._get_dependency(config, waiton=[]))
        self.assertIsNone(fsl_sub_plugin_slurm._get_dependency(config, waiton=None))
        self.assertEqual(
            'afterany:1234',
            fsl_sub_plugin_slurm._get_dependency(config, waiton=1234, array_task=True))
        with self.assertRaises(BadSubmission) as exc:
            fsl_sub_plugin_slurm._get_dependency(config, waiton={'key': 'value'})
        self.assertEqual(
            str(exc.exception), "jobhold is of unsupported type <class 'dict'>"
        )


class TestslurmFinders(unittest.TestCase):
    @patch('fsl_sub_plugin_slurm.which', autospec=True)
    def test_qstat(self, mock_which):
        bin_path = '/usr/bin/squeue'
        with self.subTest("Test 1"):
            mock_which.return_value = bin_path
            self.assertEqual(
                bin_path,
                fsl_sub_plugin_slurm._squeue_cmd()
            )
        mock_which.reset_mock()
        with self.subTest("Test 2"):
            mock_which.return_value = None
            self.assertRaises(
                fsl_sub_plugin_slurm.BadSubmission,
                fsl_sub_plugin_slurm._squeue_cmd
            )

    @patch('fsl_sub_plugin_slurm.which', autospec=True)
    def test_qsub(self, mock_which):
        bin_path = '/usr/bin/sbatch'
        with self.subTest("Test 1"):
            mock_which.return_value = bin_path
            self.assertEqual(
                bin_path,
                fsl_sub_plugin_slurm._qsub_cmd()
            )
        mock_which.reset_mock()
        with self.subTest("Test 2"):
            mock_which.return_value = None
            self.assertRaises(
                fsl_sub_plugin_slurm.BadSubmission,
                fsl_sub_plugin_slurm._qsub_cmd
            )

    @patch('fsl_sub_plugin_slurm.sp.run', autospec=True)
    def test_queue_exists(self, mock_spr):
        bin_path = '/usr/bin/sinfo'
        qname = 'myq'
        with patch(
            'fsl_sub_plugin_slurm.which',
            autospec=True,
            return_value=None
        ):
            with self.subTest("No sinfo"):
                self.assertRaises(
                    BadSubmission,
                    fsl_sub_plugin_slurm.queue_exists,
                    '123'
                )
        mock_spr.reset_mock()
        with patch(
                'fsl_sub_plugin_slurm.which',
                return_value=bin_path):

            with self.subTest("Test 1"):
                mock_spr.return_value = subprocess.CompletedProcess(
                    [bin_path, '--noheader', '-p', qname],
                    stdout='',
                    returncode=0
                )
                self.assertFalse(
                    fsl_sub_plugin_slurm.queue_exists(qname)
                )
                mock_spr.assert_called_once_with(
                    [bin_path, '--noheader', '-p', qname],
                    stdout=subprocess.PIPE,
                    check=True,
                    universal_newlines=True)
            mock_spr.reset_mock()
            with self.subTest("Test 2"):
                mock_spr.return_value = subprocess.CompletedProcess(
                    [bin_path, '--noheader', '-p', qname],
                    stdout='A   up  5-00:00:00  1   idle    anode1234\n',
                    returncode=0
                )
                self.assertTrue(
                    fsl_sub_plugin_slurm.queue_exists(qname, bin_path)
                )


@patch('fsl_sub.utils.VERSION', '1.0.0')
@patch(
    'fsl_sub_plugin_slurm.os.getcwd',
    autospec=True, return_value='/Users/testuser')
@patch(
    'fsl_sub_plugin_slurm._qsub_cmd',
    autospec=True, return_value='/usr/bin/sbatch'
)
@patch('fsl_sub_plugin_slurm.split_ram_by_slots', autospec=True)
@patch('fsl_sub_plugin_slurm.coprocessor_config', autospec=True)
@patch('fsl_sub_plugin_slurm.sp.run', autospec=True)
class TestSubmit(unittest.TestCase):
    def setUp(self):
        self.ww = tempfile.NamedTemporaryFile(
            mode='w+t',
            delete=False)
        self.now = datetime.datetime.now()
        self.strftime = datetime.datetime.strftime
        self.bash = '/bin/bash'
        os.environ['FSLSUB_SHELL'] = self.bash
        self.config = copy.deepcopy(conf_dict)
        self.mconfig = self.config['method_opts']['slurm']
        self.patch_objects = {
            'fsl_sub.utils.datetime': {'autospec': True, },
            'fsl_sub_plugin_slurm.plugin_version': {'autospec': True, 'return_value': '2.0.0', },
            'fsl_sub_plugin_slurm.loaded_modules': {'autospec': True, 'return_value': ['mymodule', ], },
            'fsl_sub_plugin_slurm.write_wrapper': {'autospec': True, 'side_effect': self.w_wrapper},
            'fsl_sub_plugin_slurm.method_config': {'autospec': True, 'return_value': self.mconfig, },
            'fsl_sub_plugin_slurm.queue_config': {'autospec': True, 'return_value': self.config.get('queues', []), },
        }
        self.patch_dict_objects = {}
        self.patches = {}
        for p, kwargs in self.patch_objects.items():
            self.patches[p] = patch(p, **kwargs)
        self.mocks = {}
        for o, p in self.patches.items():
            self.mocks[o] = p.start()

        self.dict_patches = {}
        for p, kwargs in self.patch_dict_objects.items():
            self.dict_patches[p] = patch.dict(p, **kwargs)

        for o, p in self.dict_patches.items():
            self.mocks[o] = p.start()
        self.mocks['fsl_sub.utils.datetime'].datetime.now.return_value = self.now
        self.mocks['fsl_sub.utils.datetime'].datetime.strftime = self.strftime
        self.addCleanup(patch.stopall)
        self.job_name = 'test_job'
        self.queue = 'a.q'
        self.cmd = ['./acmd', 'arg1', 'arg2', ]
        self.logdir = '/Users/testuser'
        self.jid = 12345
        self.qsub_out = str(self.jid)
        self.module = 'mymodule'
        self.log_name = os.path.join(self.logdir, self.job_name)
        self.script_head = '\n'.join(('#!' + self.bash, ''))
        self.export_str = (
            '''#SBATCH --export='''
            '''FSLSUB_JOB_ID_VAR=SLURM_JOB_ID,'''
            '''FSLSUB_ARRAYTASKID_VAR=SLURM_ARRAY_TASK_ID,'''
            '''FSLSUB_ARRAYSTARTID_VAR=SLURM_ARRAY_TASK_MIN,'''
            '''FSLSUB_ARRAYENDID_VAR=SLURM_ARRAY_TASK_MAX,'''
            '''FSLSUB_ARRAYSTEPSIZE_VAR=SLURM_ARRAY_TASK_STEP,'''
            '''FSLSUB_ARRAYCOUNT_VAR=SLURM_ARRAY_TASK_COUNT,'''
            '''FSLSUB_NSLOTS=SLURM_NPROCS''')
        self.log_str = '\n'.join((
            '#SBATCH -o {0}.o%j'.format(self.log_name),
            '#SBATCH -e {0}.e%j'.format(self.log_name),
        ))
        self.name_str = '#SBATCH --job-name=' + self.job_name
        self.chdir_str = '#SBATCH --chdir=' + self.logdir
        self.queue_str = '#SBATCH -p ' + self.queue
        self.parsable_str = '#SBATCH --parsable'
        self.requeue_str = '#SBATCH --requeue'
        self.ntasks_str = '#SBATCH --ntasks=1'
        self.nthreads_str_gpu = '#SBATCH --gpus-per-task'
        self.nthreads_str = '#SBATCH --cpus-per-task'
        self.module_load_str = 'module load ' + self.module
        self.version_str = '# Built by fsl_sub v.1.0.0 and fsl_sub_plugin_slurm v.2.0.0'
        self.sys_argv_str_base = '# Command line: '
        self.sys_argv_str = f'{self.sys_argv_str_base}fsl_sub -q {self.queue} {" ".join(self.cmd)}'
        self.submission_time_str = '# Submission time (H:M:S DD/MM/YYYY): ' + self.now.strftime("%H:%M:%S %d/%m/%Y")
        self.cmd_str = '\n'.join(('', ' '.join(self.cmd)))

    def submit_str(
            self, cmd=None, threads=1, copy_env=False,
            exports=[],
            queue=None, modules=None, host_list=[],
            project=None, module_path=None, gpu_lines=[],
            dependencies=None):
        if modules is None:
            modules = [self.module]
        if queue is None:
            queue = self.queue
        sub_str = [self.script_head, ]
        if copy_env:
            e_str = self.export_str.replace("--export=", '--export=ALL,')
        elif exports:
            e_str = self.export_str.replace("--export=", '--export=' + ','.join(exports) + ',')
        else:
            e_str = self.export_str
        sub_str.append(e_str)
        for gl in gpu_lines:
            sub_str.append('#SBATCH ' + gl)
        sub_str.append(self.log_str)
        if dependencies is not None:
            sub_str.append(f'#SBATCH --dependency={dependencies}')
        sub_str.append(self.name_str)
        sub_str.append(self.chdir_str)
        sub_str.append('#SBATCH -p ' + queue)
        if host_list:
            sub_str.append('#SBATCH -w ' + ','.join(host_list))
        sub_str.append(self.parsable_str)
        sub_str.append(self.requeue_str)
        if project is not None:
            sub_str.append('#SBATCH --account ' + project)
        sub_str.append(self.ntasks_str)
        if threads > 1:
            if gpu_lines:
                threading = self.nthreads_str_gpu
            else:
                threading = self.nthreads_str
            sub_str.append("=".join((threading, str(threads))))
        if module_path is not None:
            sub_str.append('MODULEPATH={0}:$MODULEPATH'.format(module_path))
        for module in modules:
            sub_str.append('module load ' + module)
        sub_str.append(self.version_str)
        if cmd is None:
            sub_str.append(self.sys_argv_str)
        else:
            sub_str.append(f'{self.sys_argv_str_base}{cmd}')
        sub_str.append(self.submission_time_str)
        sub_str.append('\n'.join(('', ' '.join(self.cmd))))
        sub_str.append('')
        return '\n'.join(sub_str)

    def TearDown(self):
        self.ww.close()
        os.unlink(self.ww.name)
        patch.stopall()

    plugin = fsl_sub_plugin_slurm

    def w_wrapper(self, content):
        for lf in content:
            self.ww.write(lf + '\n')
        return self.ww.name

    def test_empty_submit(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        self.assertRaises(
            self.plugin.BadSubmission,
            self.plugin.submit,
            None, None, None
        )

    def test_submit_basic(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        with self.subTest("Slurm"):
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str()
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=self.queue
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_submit_dependencies(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        with self.subTest("Slurm"):
            expected_cmd = ['/usr/bin/sbatch']

            cmd_argv_base = ['fsl_sub', '-q', self.queue, ]
            with self.subTest('Basic dependency'):
                cmd_argv = copy.copy(cmd_argv_base)
                jh = '1234'
                cmd_argv.extend(['-j', '1234', ])
                cmd_argv.extend(self.cmd)
                expected_script = self.submit_str(
                    cmd=f'{" ".join(cmd_argv)}',
                    dependencies=f"afterany:{jh}")
                mock_sprun.reset_mock()
                mock_sprun.return_value = subprocess.CompletedProcess(
                    expected_cmd, 0,
                    stdout=self.qsub_out, stderr=None)

                with patch('fsl_sub.utils.sys.argv', cmd_argv):
                    self.assertEqual(
                        self.jid,
                        self.plugin.submit(
                            command=self.cmd,
                            job_name=self.job_name,
                            queue=self.queue,
                            jobhold=jh
                        )
                    )
                mock_sprun.assert_called_once_with(
                    expected_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    input=expected_script
                )
            with self.subTest('Complex dependency'):
                cmd_argv = copy.copy(cmd_argv_base)
                jh = 'afterany:1234:afternotok:1345'
                cmd_argv.extend(['-j', jh, ])
                cmd_argv.extend(self.cmd)
                expected_script = self.submit_str(
                    cmd=f'{" ".join(cmd_argv)}',
                    dependencies=jh)
                mock_sprun.reset_mock()
                mock_sprun.return_value = subprocess.CompletedProcess(
                    expected_cmd, 0,
                    stdout=self.qsub_out, stderr=None)
                with patch('fsl_sub.utils.sys.argv', cmd_argv):
                    self.assertEqual(
                        self.jid,
                        self.plugin.submit(
                            command=self.cmd,
                            job_name=self.job_name,
                            queue=self.queue,
                            jobhold=jh
                        )
                    )
                mock_sprun.assert_called_once_with(
                    expected_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    input=expected_script
                )

    def test_submit_basic_export_vars(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        with self.subTest("Slurm"):
            self.mconfig['export_vars'] = ['FSLTEST']
            self.mconfig['copy_environment'] = False
            self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = self.mconfig

            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(exports=['FSLTEST'])
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=self.queue
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_submit_singlehost(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        queue = 'a.q@host1'
        pure_q = 'a.q'
        with self.subTest("Slurm"):
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(queue=pure_q, host_list=['host1', ])
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=queue
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_submit_multiq(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        queue = ['a.q', 'b.q', ]
        with self.subTest("Slurm"):
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(
                cmd='fsl_sub -q ' + ','.join(queue) + ' ' + ' '.join(self.cmd),
                queue=','.join(queue))
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '-q', ','.join(queue), ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=','.join(queue)
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_submit_multiq_multih(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        queue = ['a.q@host1', 'b.q', ]
        pure_q = ['a.q', 'b.q']
        hostlist = ['host1', ]
        with self.subTest("Slurm"):
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(
                cmd='fsl_sub -q ' + ','.join(queue) + ' ' + ' '.join(self.cmd),
                queue=','.join(pure_q),
                host_list=hostlist)
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '-q', ','.join(queue), ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=','.join(queue)
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_submit_multiq_multih2(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        queue = ['a.q@host1', 'b.q@host2', ]
        hostlist = ['host1', 'host2']
        pure_q = ','.join([q.split('@')[0] for q in queue])
        with self.subTest("Slurm"):
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(
                cmd='fsl_sub -q ' + ','.join(queue) + ' ' + ' '.join(self.cmd),
                queue=pure_q,
                host_list=hostlist)
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '-q', ','.join(queue), ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=queue
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_project_submit(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        project = 'Aproject'
        with self.subTest("No projects"):
            w_conf = copy.deepcopy(self.config)
            w_conf['method_opts']['slurm']['projects'] = True
            self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str()
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=self.queue
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )
        mock_sprun.reset_mock()
        self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = mconf_dict
        with self.subTest("With Project"):
            cmd_argv = ['fsl_sub', '-q', self.queue, '--project', project]
            cmd_argv.extend(self.cmd)
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(
                cmd=' '.join(cmd_argv),
                project=project)
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=self.queue,
                        project=project
                    )
                )
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_modulepath_submit(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        w_conf = copy.deepcopy(self.config)
        w_conf['method_opts']['slurm']['projects'] = True
        w_conf['method_opts']['slurm']['add_module_paths'] = ['/usr/local/shellmodules']
        self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
        mod_path = '/usr/local/shellmodules'
        expected_cmd = ['/usr/bin/sbatch']
        expected_script = self.submit_str(module_path=mod_path)
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 0,
            stdout=self.qsub_out, stderr=None)
        cmd_argv = ['fsl_sub', '-q', self.queue, ]
        cmd_argv.extend(self.cmd)
        with patch('fsl_sub.utils.sys.argv', cmd_argv):
            self.assertEqual(
                self.jid,
                self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                )
            )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            input=expected_script
        )

    def test_GPU(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        with self.subTest("GPU with constraints"):
            w_conf = copy.deepcopy(self.config)
            w_conf['copro_opts']['cuda']['class_constraint'] = False
            self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
            mock_cpconf.return_value = w_conf['copro_opts']['cuda']
            cmd_argv = ['fsl_sub', '--coprocessor', 'cuda', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(
                cmd=' '.join(cmd_argv),
                gpu_lines=['--gres=gpu:k80:1', ])
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '--coprocessor', 'cuda', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                job_id = self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                    coprocessor='cuda'
                )
                self.assertEqual(self.jid, job_id)
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

        mock_sprun.reset_mock()
        mock_sprun.reset_mock()
        with self.subTest("GPU without constraints"):
            w_conf = copy.deepcopy(self.config)
            w_conf['copro_opts']['cuda']['classes'] = False
            self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
            mock_cpconf.return_value = w_conf['copro_opts']['cuda']
            cmd_argv = ['fsl_sub', '--coprocessor', 'cuda', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(
                cmd=' '.join(cmd_argv),
                gpu_lines=['--gres=gpu:1', ])
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            cmd_argv = ['fsl_sub', '--coprocessor', 'cuda', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                job_id = self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                    coprocessor='cuda'
                )
                self.assertEqual(self.jid, job_id)
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

        mock_sprun.reset_mock()
        with self.subTest("With GPU constraints"):
            w_conf = self.config
            w_conf['copro_opts']['cuda']['set_visible'] = True
            w_conf['copro_opts']['cuda']['class_constraint'] = 'gpu_sku'
            self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
            mock_cpconf.return_value = w_conf['copro_opts']['cuda']
            cmd_argv = ['fsl_sub', '--coprocessor', 'cuda', '-q', self.queue, ]
            cmd_argv.extend(self.cmd)
            expected_cmd = ['/usr/bin/sbatch']
            expected_script = self.submit_str(
                cmd=' '.join(cmd_argv),
                gpu_lines=[
                    '--constraint="k80|p100"',
                    '--gres=gpu:1', ])
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                job_id = self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                    coprocessor='cuda'
                )
                self.assertEqual(self.jid, job_id)
            mock_sprun.assert_called_once_with(
                expected_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                input=expected_script
            )

    def test_submit_wrapper_copy_env(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        w_conf = self.config
        w_conf['method_opts']['slurm']['copy_environment'] = True
        w_conf['method_opts']['slurm']['preserve_modules'] = False
        self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']

        expected_cmd = ['/usr/bin/sbatch']
        expected_script = self.submit_str(copy_env=True, modules=[])
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 0,
            stdout=self.qsub_out, stderr=None)
        cmd_argv = ['fsl_sub', '-q', self.queue, ]
        cmd_argv.extend(self.cmd)
        with patch('fsl_sub.utils.sys.argv', cmd_argv):
            self.assertEqual(
                self.jid,
                self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue
                )
            )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            input=expected_script
        )
        mock_sprun.reset_mock()

    def test_submit_wrapper_set_complex_vars(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        w_conf = self.config
        w_conf['method_opts']['slurm']['copy_environment'] = False
        self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
        cmd_argv = ['fsl_sub', '-q', self.queue, "--export='AVAR=\'1,2\''", "--export='BVAR=\'a b\'", ]
        cmd_argv.extend(self.cmd)

        expected_cmd = ['/usr/bin/sbatch']
        expected_script = self.submit_str(
            cmd=' '.join(cmd_argv),
            exports=["AVAR='1,2'", "BVAR='a b'", ])
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 0,
            stdout=self.qsub_out, stderr=None)
        with patch('fsl_sub.utils.sys.argv', cmd_argv):
            self.assertEqual(
                self.jid,
                self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                    export_vars=['AVAR=1,2', 'BVAR=a b']
                )
            )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            input=expected_script
        )
        mock_sprun.reset_mock()

    def test_submit_wrapper_keep(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        w_conf = self.config
        w_conf['method_opts']['slurm']['keep_jobscript'] = True
        w_conf['method_opts']['slurm']['copy_environment'] = False
        self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
        mock_cpconf.return_value = w_conf['copro_opts']['cuda']
        cmd_argv = ['fsl_sub', '-q', self.queue, ]
        cmd_argv.extend(self.cmd)

        expected_cmd = ['/usr/bin/sbatch', self.ww.name]
        expected_script = self.submit_str()
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 0,
            stdout=self.qsub_out, stderr=None)

        with patch('fsl_sub_plugin_slurm.os.rename') as mock_rename:
            with patch('fsl_sub.utils.sys.argv', cmd_argv):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        command=self.cmd,
                        job_name=self.job_name,
                        queue=self.queue,
                        keep_jobscript=True
                    )
                )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        mock_sprun.reset_mock()
        self.ww.seek(0)
        wrapper_lines = self.ww.read().splitlines()
        self.maxDiff = None
        self.assertListEqual(
            wrapper_lines,
            expected_script.split('\n')
        )
        mock_rename.assert_called_once_with(
            self.ww.name,
            os.path.join(
                os.getcwd(),
                '_'.join(('wrapper', str(self.jid) + '.sh'))
            )
        )

    def test_submit_wrapper_keep_with_error(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        w_conf = self.config
        w_conf['method_opts']['slurm']['keep_jobscript'] = True
        w_conf['method_opts']['slurm']['copy_environment'] = False
        self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
        mock_cpconf.return_value = w_conf['copro_opts']['cuda']
        cmd_argv = ['fsl_sub', '-q', self.queue, ]
        cmd_argv.extend(self.cmd)

        expected_cmd = ['/usr/bin/sbatch', self.ww.name]
        expected_script = self.submit_str()
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 1,
            stdout=self.qsub_out, stderr="An error")
        mock_now = datetime.datetime.now()

        with patch('fsl_sub_plugin_slurm.os.rename') as mock_rename:
            with patch('fsl_sub.utils.sys.argv', cmd_argv):

                with patch('fsl_sub_plugin_slurm.datetime', wraps=datetime) as mock_time:
                    mock_time.datetime.now.return_value = mock_now
                    with self.assertRaises(fsl_sub.exceptions.BadSubmission) as ex:
                        self.plugin.submit(
                            command=self.cmd,
                            job_name=self.job_name,
                            queue=self.queue,
                            keep_jobscript=True
                        )

                message = str(ex.exception)
                self.assertEqual(message, "An error")
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        mock_sprun.reset_mock()
        self.ww.seek(0)
        wrapper_lines = self.ww.read().splitlines()
        self.maxDiff = None
        self.assertListEqual(
            wrapper_lines,
            expected_script.split('\n')
        )
        mock_rename.assert_called_once_with(
            self.ww.name,
            os.path.join(
                os.getcwd(),
                '_'.join(('wrapper_failed', str(mock_now.strftime("%d-%b-%Y_%H%M%S")) + '.sh'))
            )
        )

    def test_submit_script(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        w_conf = self.config
        w_conf['method_opts']['slurm']['keep_jobscript'] = True
        w_conf['method_opts']['slurm']['copy_environment'] = False
        self.mocks['fsl_sub_plugin_slurm.method_config'].return_value = w_conf['method_opts']['slurm']
        mock_cpconf.return_value = w_conf['copro_opts']['cuda']

        with tempfile.NamedTemporaryFile() as tf:

            expected_cmd = ['/usr/bin/sbatch', tf.name]
            mock_sprun.return_value = subprocess.CompletedProcess(
                expected_cmd, 0,
                stdout=self.qsub_out, stderr=None)

            with patch('fsl_sub.utils.sys.argv', ['fsl_sub', '--usescript', tf.name]):
                self.assertEqual(
                    self.jid,
                    self.plugin.submit(
                        [tf.name],
                        usescript=True,
                    )
                )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

    def test_submit_threads_gecompat(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        cmd_argv = ['fsl_sub', '-q', self.queue, '-s', 'threads,2', ]
        cmd_argv.extend(self.cmd)
        expected_cmd = ['/usr/bin/sbatch']
        expected_script = self.submit_str(
            threads=2,
            cmd=' '.join(cmd_argv))
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 0,
            stdout=self.qsub_out, stderr=None)
        with patch('fsl_sub.utils.sys.argv', cmd_argv):
            self.assertEqual(
                self.jid,
                self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                    threads=2,
                    parallel_env=None
                )
            )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            input=expected_script
        )

    def test_submit_threads(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        cmd_argv = ['fsl_sub', '-q', self.queue, '-s', '2', ]
        cmd_argv.extend(self.cmd)
        expected_cmd = ['/usr/bin/sbatch']
        expected_script = self.submit_str(
            threads=2,
            cmd=' '.join(cmd_argv))
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 0,
            stdout=self.qsub_out, stderr=None)
        with patch('fsl_sub.utils.sys.argv', cmd_argv):
            self.assertEqual(
                self.jid,
                self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                    threads=2,
                    parallel_env=None
                )
            )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            input=expected_script
        )

    def test_submit_threads_gpu(
            self, mock_sprun, mock_cpconf,
            mock_srbs, mock_qsub,
            mock_getcwd):
        cmd_argv = ['fsl_sub', '-q', self.queue, '-s', '2', ]
        cmd_argv.extend(self.cmd)
        self.mocks['fsl_sub_plugin_slurm.queue_config'].return_value = {
            'a.q': {'copros': ['cuda', ], },
        }
        expected_cmd = ['/usr/bin/sbatch']
        expected_script = self.submit_str(
            threads=2,
            cmd=' '.join(cmd_argv))
        mock_sprun.return_value = subprocess.CompletedProcess(
            expected_cmd, 0,
            stdout=self.qsub_out, stderr=None)
        with patch('fsl_sub.utils.sys.argv', cmd_argv):
            self.assertEqual(
                self.jid,
                self.plugin.submit(
                    command=self.cmd,
                    job_name=self.job_name,
                    queue=self.queue,
                    threads=2,
                    parallel_env=None
                )
            )
        mock_sprun.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            input=expected_script
        )


class TestQdel(unittest.TestCase):
    @patch('fsl_sub_plugin_slurm.which', autospec=True)
    @patch('fsl_sub_plugin_slurm.sp.run', autospec=True)
    def testqdel(self, mock_spr, mock_which):
        pid = 1234
        mock_which.return_value = '/usr/bin/scancel'
        mock_spr.return_value = subprocess.CompletedProcess(
            ['/usr/bin/cancel', str(pid)],
            0,
            'Job ' + str(pid) + ' deleted',
            ''
        )
        self.assertTupleEqual(
            fsl_sub_plugin_slurm.qdel(pid),
            ('Job ' + str(pid) + ' deleted', 0)
        )
        mock_spr.assert_called_once_with(
            ['/usr/bin/scancel', str(pid)],
            universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )


class TestJobStatus(unittest.TestCase):
    def setUp(self):
        self.QUEUED = 0
        self.RUNNING = 1
        self.FINISHED = 2
        self.FAILED = 3
        self.HELD = 4
        self.REQUEUED = 5
        self.RESTARTED = 6
        self.SUSPENDED = 7
        self.STARTING = 8

        self.REPORTING = [
            'Queued',
            'Running',
            'Finished',
            'Failed',
            'Held',
            'Requeued',
            'Restarted',
            'Suspended',
            'Starting'
        ]

        self.sacct_finished_out = (
            '''123456|myjob|2017-10-16T05:28:38|2017-10-16T05:29:24|2017-10-16T06:25:45|'''
            '''COMPLETED|0:0|''')
        self.sacct_finished_job = {
            'id': 123456,
            'name': 'myjob',
            'sub_time': datetime.datetime(2017, 10, 16, 5, 28, 38),
            'tasks': {
                1: {
                    'status': self.FINISHED,
                    'start_time': datetime.datetime(2017, 10, 16, 5, 29, 24),
                    'end_time': datetime.datetime(2017, 10, 16, 6, 25, 45),
                },
            },
        }
        self.sacct_failedbatch_out = (
            '''123456|feat|2020-10-19T12:00:49|2020-10-19T12:00:51|2020-10-19T12:15:07|FAILED|1:0
123456.batch|batch|2020-10-19T12:00:51|2020-10-19T12:00:51|2020-10-19T12:15:07|FAILED|1:0''')
        self.sacct_failedbatch_job = {
            'id': 123456,
            'name': 'feat',
            'sub_time': datetime.datetime(2020, 10, 19, 12, 00, 49),
            'tasks': {
                1: {
                    'status': self.FAILED,
                    'start_time': datetime.datetime(2020, 10, 19, 12, 00, 51),
                    'end_time': datetime.datetime(2020, 10, 19, 12, 15, 7),
                },
            },
        }
        self.expected_keys = [
            'id', 'name', 'sub_time', 'tasks',
        ]
        self.expected_keys.sort()

        self.task_expected_keys = [
            'status', 'start_time', 'end_time',
        ]
        self.task_expected_keys.sort()

        self.slurm_example_sacct = (
            '''1716106|acctest|2018-06-05T09:42:24|2018-06-05T09:42:24|'''
            '''2018-06-05T09:44:08|COMPLETED|0:0
1716106.batch|batch|2018-06-05T09:42:24|2018-06-05T09:42:24|'''
            '''2018-06-05T09:44:08|COMPLETED|0:0
''')

    @patch('fsl_sub_plugin_slurm._sacct_cmd', return_value='/usr/bin/sacct')
    def test_job_status(self, mock_qacct):
        self.maxDiff = None
        with patch('fsl_sub_plugin_slurm.sp.run', autospec=True) as mock_sprun:

            with self.subTest('No sacct'):
                mock_sprun.side_effect = FileNotFoundError
                self.assertRaises(
                    BadSubmission,
                    fsl_sub_plugin_slurm._get_sacct,
                    1716106)
            mock_sprun.reset_mock()
            mock_sprun.side_effect = None
            with self.subTest('No job'):
                mock_sprun.return_value = subprocess.CompletedProcess(
                    '/usr/bin/sacct',
                    stdout='',
                    stderr='',
                    returncode=0
                )
                self.assertRaises(
                    UnknownJobId,
                    fsl_sub_plugin_slurm._get_sacct,
                    1716106)
            mock_sprun.reset_mock()
            with self.subTest('Single job'):
                mock_sprun.return_value = subprocess.CompletedProcess(
                    '/usr/bin/sacct',
                    stdout=self.slurm_example_sacct,
                    returncode=0
                )
                self.assertDictEqual(
                    fsl_sub_plugin_slurm._get_sacct(1716106),
                    {
                        'id': 1716106,
                        'name': 'acctest',
                        'sub_time': datetime.datetime(
                            2018, 6, 5, 9, 42, 24),
                        'tasks': {
                            1: {
                                'start_time': datetime.datetime(
                                    2018, 6, 5, 9, 42, 24),
                                'end_time': datetime.datetime(
                                    2018, 6, 5, 9, 44, 8),
                                'status': fsl_sub.consts.FINISHED,
                            }
                        }
                    }
                )
        with self.subTest("Completed"):
            with patch('fsl_sub_plugin_slurm.sp.run', autospec=True) as mock_sprun:
                mock_sprun.return_value = subprocess.CompletedProcess(
                    ['sacct'], 0, self.sacct_finished_out, '')
                job_stat = fsl_sub_plugin_slurm.job_status(123456)
            output_keys = list(job_stat.keys())
            output_keys.sort()
            self.assertListEqual(output_keys, self.expected_keys)
            task_output_keys = list(job_stat['tasks'][1].keys())
            task_output_keys.sort()
            self.assertListEqual(task_output_keys, self.task_expected_keys)
            self.assertDictEqual(job_stat, self.sacct_finished_job)

        with self.subTest("Running"):
            with patch('fsl_sub_plugin_slurm.sp.run', autospec=True) as mock_sprun:
                mock_sprun.return_value = subprocess.CompletedProcess(
                    ['sacct'], 0, self.sacct_failedbatch_out, '')
                job_stat = fsl_sub_plugin_slurm.job_status(123456)
            output_keys = list(job_stat.keys())
            output_keys.sort()
            self.assertListEqual(output_keys, self.expected_keys)
            task_output_keys = list(job_stat['tasks'][1].keys())
            task_output_keys.sort()
            self.assertListEqual(task_output_keys, self.task_expected_keys)
            self.assertDictEqual(job_stat, self.sacct_failedbatch_job)


class TestQueueCapture(unittest.TestCase):
    def setUp(self):
        self.sinfo_f_one_h = '''os:centos7,
'''
        self.sinfo_f_two_h = (
            '''gpu,'''
            '''gpu_sku:P100,
            gpu,'''
            '''gpu_sku:V100,
''')
        self.sinfo_s = '''htc*\n'''
        self.sinfo_G_two_h = 'gpu:p100:4(S:0-1)\ngpu:v100:8(S:0-1)'
        self.sinfo_G_one_h = '(null)'
        self.sinfo_G_no_parens = 'gpu:gtx:2'
        self.sinfo_G_no_type = 'gpu:2(S:0-1)'
        self.sinfo_G_multiplier = 'gpu:2K(S:0-2023)'
        self.sinfo_G_list = 'gpu:p100:2(S:0-1),gpu:v100:2(S:0-1)'
        self.sinfo_O_one_h = '''8                  UNLIMITED           64000             1-00:00:00          htc-node1
'''
        self.sinfo_O_one_h_inf = '''8                  UNLIMITED           64000             infinite          htc-node1
'''
        self.sinfo_O_two_h = ('''8                   UNLIMITED           384000               1-00:00:00          '''
                              '''htc-gpu1
16                 UNLIMITED           512000               5-00:00:00          htc-gpu2
''')

    @patch('fsl_sub_plugin_slurm._sinfo_cmd', return_value='/usr/bin/sinfo')
    def test__get_queue_gres(self, mock_sinfo):
        with patch('fsl_sub_plugin_slurm.sp.run') as mock_spr:
            with self.subTest('No Type'):
                mock_spr.return_value = subprocess.CompletedProcess(
                    ['sinfo', '%G', ], 0, self.sinfo_G_no_type
                )
                gres = fsl_sub_plugin_slurm._get_queue_gres('htc')
                self.assertDictEqual(
                    gres,
                    {'gpu': [('-', 2)]})
            with self.subTest("Multiplier"):
                mock_spr.return_value = subprocess.CompletedProcess(
                    ['sinfo', '%G', ], 0, self.sinfo_G_multiplier
                )
                gres = fsl_sub_plugin_slurm._get_queue_gres('htc')
                self.assertDictEqual(
                    gres,
                    {'gpu': [('-', 2048)]})
            with self.subTest("No Parens"):
                mock_spr.return_value = subprocess.CompletedProcess(
                    ['sinfo', '%G', ], 0, self.sinfo_G_no_parens
                )
                gres = fsl_sub_plugin_slurm._get_queue_gres('htc')
                self.assertDictEqual(
                    gres,
                    {'gpu': [('gtx', 2), ]})
            with self.subTest("List"):
                mock_spr.return_value = subprocess.CompletedProcess(
                    ['sinfo', '%G', ], 0, self.sinfo_G_list
                )
                gres = fsl_sub_plugin_slurm._get_queue_gres('htc')
                self.assertDictEqual(
                    gres,
                    {'gpu': [('p100', 2), ('v100', 2), ]})
            with self.subTest("No GRES"):
                mock_spr.return_value = subprocess.CompletedProcess(
                    ['sinfo', '%G', ], 0, self.sinfo_G_one_h
                )
                gres = fsl_sub_plugin_slurm._get_queue_gres('htc')
                self.assertDictEqual(gres, defaultdict(list))
            with self.subTest('Two hosts'):
                mock_spr.return_value = subprocess.CompletedProcess(
                    ['sinfo', '%G', ], 0, self.sinfo_G_two_h
                )
                gres = fsl_sub_plugin_slurm._get_queue_gres('htc')
                self.assertDictEqual(gres, {'gpu': [('p100', 4, ), ('v100', 8, ), ], })

    @patch('fsl_sub_plugin_slurm._sinfo_cmd', return_value='/usr/bin/sinfo')
    def test__get_queue_info(self, mock_sinfo):
        with patch('fsl_sub_plugin_slurm.sp.run') as mock_spr:
            mock_spr.return_value = subprocess.CompletedProcess(
                ['sinfo', '%f', ], 0, self.sinfo_O_one_h
            )
            (qdef, comments) = fsl_sub_plugin_slurm._get_queue_info('htc')
            self.assertDictEqual(
                qdef,
                {
                    'cpus': 8,
                    'memory': 64,
                    'qname': 'htc',
                    'qtime': 1440,
                })
        with patch('fsl_sub_plugin_slurm.sp.run') as mock_spr:
            mock_spr.return_value = subprocess.CompletedProcess(
                ['sinfo', '%f', ], 0, self.sinfo_O_one_h_inf
            )
            (qdef, comments) = fsl_sub_plugin_slurm._get_queue_info('htc')
            self.assertDictEqual(
                qdef,
                {
                    'cpus': 8,
                    'memory': 64,
                    'qname': 'htc',
                    'qtime': 527039,
                })

    @patch('fsl_sub_plugin_slurm._sinfo_cmd', return_value='/usr/bin/sinfo')
    def test__get_queue_features(self, mock_sinfo):
        with patch('fsl_sub_plugin_slurm.sp.run') as mock_spr:
            mock_spr.return_value = subprocess.CompletedProcess(
                ['sinfo', '%f', ], 0, self.sinfo_f_one_h
            )
            features = fsl_sub_plugin_slurm._get_queue_features('htc')
            self.assertDictEqual(features, {'os': ['centos7', ], })
        with patch('fsl_sub_plugin_slurm.sp.run') as mock_spr:
            mock_spr.return_value = subprocess.CompletedProcess(
                ['sinfo', '%f', ], 0, self.sinfo_f_two_h
            )
            features = fsl_sub_plugin_slurm._get_queue_features('htc')
            self.assertDictEqual(features, {'gpu': [], 'gpu_sku': ['P100', 'V100'], })

    @patch('fsl_sub_plugin_slurm._sinfo_cmd', return_value='/usr/bin/sinfo')
    @patch('fsl_sub_plugin_slurm.method_config', return_value=conf_dict['method_opts']['slurm'])
    def test_build_queue_defs(self, mock_mconf, mock_sinfo):
        with patch('fsl_sub_plugin_slurm.sp.run') as mock_spr:
            mock_spr.side_effect = (
                subprocess.CompletedProcess(
                    ['sinfo', '-s', ], 0, self.sinfo_s
                ),
                subprocess.CompletedProcess(
                    ['sinfo', '%O', ], 0, self.sinfo_O_one_h
                ),
                subprocess.CompletedProcess(
                    ['sinfo', '%G', ], 0, self.sinfo_G_one_h
                ),
                subprocess.CompletedProcess(
                    ['sinfo', '%f', ], 0, self.sinfo_f_one_h
                )
            )
            qdefs = fsl_sub_plugin_slurm.build_queue_defs()
            yaml = YAML()
            yaml.width = 128
        expected_yaml = yaml.load('''queues:
  htc: # Queue name
  # default: true # Is this the default partition?
  # priority: 1 # Priority in group - higher wins
  # group: 1 # Group partitions with the same integer then order by priority
    time: 1440 # Maximum job run time in minutes
    max_slots: 8 # Maximum number of threads/slots on a queue
    max_size: 64 # Maximum RAM size of a job in {0}B
    slot_size: Null # Slot size is normally irrelevant on SLURM - set this to memory (in {0}B) per thread if required
'''.format(fsl_sub.consts.RAMUNITS))
        qd_str = io.StringIO()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.representer.add_representer(type(None), yaml_repr_none)
        yaml.dump(qdefs, qd_str)
        eq_str = io.StringIO()
        yaml.dump(expected_yaml, eq_str)
        self.maxDiff = None
        self.assertEqual(qd_str.getvalue(), eq_str.getvalue())
        with self.subTest("Two hosts"):
            with patch('fsl_sub_plugin_slurm.sp.run') as mock_spr:
                mock_spr.side_effect = (
                    subprocess.CompletedProcess(
                        ['sinfo', '-s', ], 0, self.sinfo_s
                    ),
                    subprocess.CompletedProcess(
                        ['sinfo', '%O', ], 0, self.sinfo_O_two_h
                    ),
                    subprocess.CompletedProcess(
                        ['sinfo', '%G', ], 0, self.sinfo_G_two_h
                    ),
                    subprocess.CompletedProcess(
                        ['sinfo', '%f', ], 0, self.sinfo_f_two_h
                    )
                )
                qdefs = fsl_sub_plugin_slurm.build_queue_defs()
                yaml = YAML()
                yaml.width = 128
            expected_yaml = yaml.load(
                '''queues:
  htc: # Queue name
  # Partition contains nodes with different numbers of CPUs
  # Partition contains nodes with different amounts of memory, consider switching on RAM nofitication
  # Partition contains nodes with differing maximum run times, consider switching on time notification
  # default: true # Is this the default partition?
  # priority: 1 # Priority in group - higher wins
  # group: 1 # Group partitions with the same integer then order by priority
    time: 7200 # Maximum job run time in minutes
    max_slots: 16 # Maximum number of threads/slots on a queue
    max_size: 512 # Maximum RAM size of a job in {0}B
    slot_size: Null # Slot size is normally irrelevant on SLURM - set this to memory (in {0}B) per thread if required
# CUDA Co-processor available
    copros:
      cuda:
        max_quantity: 8 # Maximum available per node
        exclusive: false # Does this only run jobs requiring this co-processor?
# Partition features that look like GPU resource constraints, so
# you could use these resource/classes:
# If resource is 'gpu_sku':
#       classes:
#         - P100
#         - V100
# Default, using 'gpu' resource:
        classes:
          - p100
          - v100
coproc_opts:
  # Partitions with a GRES 'gpu' indicate the presence of GPUs
  # See below for possible top-level coproc_opts configuration - this will need verifying before use
  cuda:
    resource: gpu
    include_more_capable: false # Should we also allow running on more capable hardware? Requires constraints to be used
    classes: true
# Features found that might be selectors for GPUs, alternate class definitions
# would be:
# With a copros: cuda: resource of 'gpu_sku'
#   class_types:
#     P100:
#       resource: P100
#       doc: Request P100
#       capability: 4
#     V100:
#       resource: V100
#       doc: Request V100
#       capability: 5
    class_types:
      p100: # Short code for the type of coprocessor - used on the command line and in queue definition
        resource: p100 # Queue resource to request
        doc: Request p100
        capability: 4 # p100
      v100: # Short code for the type of coprocessor - used on the command line and in queue definition
        resource: v100 # Queue resource to request
        doc: Request v100
        capability: 5 # v100
'''.format(fsl_sub.consts.RAMUNITS))
            qd_str = io.StringIO()
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.representer.add_representer(type(None), yaml_repr_none)
            yaml.dump(qdefs, qd_str)
            eq_str = io.StringIO()
            yaml.dump(expected_yaml, eq_str)
            self.maxDiff = None
            self.assertEqual(qd_str.getvalue(), eq_str.getvalue())


if __name__ == '__main__':
    unittest.main()
