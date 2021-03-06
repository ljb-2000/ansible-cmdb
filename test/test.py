import sys
import unittest
import imp
import os

sys.path.insert(0, '../lib')
ansiblecmdb = imp.load_source('ansiblecmdb', '../src/ansible-cmdb')

class ExtendTestCase(unittest.TestCase):
    """
    Test the extending of facts.
    """
    def testExtendOverrideParams(self):
        """
        Test that we can override a native fact
        """
        fact_dirs = ['f_extend/out_setup', 'f_extend/extend']
        ansible = ansiblecmdb.Ansible(fact_dirs)
        env_editor = ansible.hosts['debian.dev.local']['ansible_facts']['ansible_env']['EDITOR']
        self.assertEqual(env_editor, 'nano')

    def testExtendAddParams(self):
        """
        Test that we can add new facts
        """
        fact_dirs = ['f_extend/out_setup', 'f_extend/extend']
        ansible = ansiblecmdb.Ansible(fact_dirs)
        software = ansible.hosts['debian.dev.local']['software']
        self.assertIn('Apache2', software)

class HostParseTestCase(unittest.TestCase):
    """
    Test the hosts inventory parser
    """
    def testChildGroupHosts(self):
        """
        Test that children groups contain all hosts they should.
        """
        fact_dirs = ['f_hostparse/out']
        inventory = 'f_hostparse/hosts'
        ansible = ansiblecmdb.Ansible(fact_dirs, inventory)
        groups = ansible.hosts['db.dev.local']['groups']
        self.assertIn('db', groups)
        self.assertIn('dev', groups)
        self.assertIn('dev_local', groups)

    def testChildGroupVars(self):
        """
        Test that all vars applied against a child group are set on the hosts.
        """
        fact_dirs = ['f_hostparse/out']
        inventory = 'f_hostparse/hosts'
        ansible = ansiblecmdb.Ansible(fact_dirs, inventory)
        host_vars = ansible.hosts['db.dev.local']['hostvars']
        self.assertEqual(host_vars['function'], 'db')
        self.assertEqual(host_vars['dtap'], 'dev')

    def testHostsDir(self):
        """
        Verify that we can specify a directory as the hosts inventory file and
        that all files are parsed.
        """
        fact_dirs = ['f_hostparse/out']
        inventory = 'f_hostparse/hostsdir'
        ansible = ansiblecmdb.Ansible(fact_dirs, inventory)
        host_vars = ansible.hosts['db.dev.local']['hostvars']
        groups = ansible.hosts['db.dev.local']['groups']
        self.assertEqual(host_vars['function'], 'db')
        self.assertIn('db', groups)

    def testExpandHostDef(self):
        """
        Verify that host ranges are properly expanded. E.g. db[01-03].local ->
        db01.local, db02.local, db03.local.
        """
        fact_dirs = ['f_hostparse/out']
        inventory = 'f_hostparse/hosts'
        ansible = ansiblecmdb.Ansible(fact_dirs, inventory)
        self.assertIn('web02.dev.local', ansible.hosts)

class FactCacheTestCase(unittest.TestCase):
    """
    Test that we properly read fact-cached output dirs.
    """
    def testFactCache(self):
        fact_dirs = ['f_factcache/out']
        inventory = 'f_factcache/hosts'
        ansible = ansiblecmdb.Ansible(fact_dirs, inventory, fact_cache=True)
        host_vars = ansible.hosts['debian.dev.local']['hostvars']
        groups = ansible.hosts['debian.dev.local']['groups']
        ansible_facts = ansible.hosts['debian.dev.local']['ansible_facts']
        self.assertIn('dev', groups)
        self.assertEqual(host_vars['dtap'], 'dev')
        self.assertIn('ansible_env', ansible_facts)

class DynInvTestCase(unittest.TestCase):
    """
    Test dynamic inventory execution and parsing
    """
    def testParse(self):
        fact_dirs = ['f_hostparse/out'] # Reuse f_hostparse
        inventory = 'f_dyninv/dyninv.py'
        ansible = ansiblecmdb.Ansible(fact_dirs, inventory)
        self.assertIn('host5.example.com', ansible.hosts)
        host_vars = ansible.hosts['host5.example.com']['hostvars']
        groups = ansible.hosts['host5.example.com']['groups']
        self.assertEqual(host_vars['b'], False)
        self.assertIn("atlanta", groups)

if __name__ == '__main__':
    unittest.main(exit=False)

    try:
        os.unlink('../src/ansible-cmdbc') # FIXME: Where is this coming from? Our weird import I assume.
    except Exception:
        pass
