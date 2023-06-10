import os
import subprocess

from pyplease import modules

class Module(modules.Module):
    """Ssh configurator

    Useful for generating keys etc."""

    @modules.action
    def generate_key(self, args):
        """generates a keypair"""

        self.extra_params(args)
        
        self.prepare_folder()

        if os.path.exists(self.normalize_path('~/.ssh/id_dsa')):
            return self.failure('~/.ssh/id_dsa key already exists!')

        p = subprocess.Popen(['ssh-keygen', '-t', 'dsa']).wait()

        if not p:
            self.success('Seems like the key was generated!')
        else:
            self.failure('Exit code: %s' % p)


    @modules.action
    def authorize(self, args):
        """allows login with a key (adds it to authorized_keys)"""
        self.prepare_folder()

        if args:
            key = args[0]
            self.extra_params(args[1:])
        else:
            key = self.ask('Public key?', validate=self.validate_not_blank)

        path = self.normalize_path('~/.ssh/authorized_keys')

        if os.path.exists(path) and self.has_line(path, key):
            return self.failure('Already in authorized')

        self.append(path, '%s\n' % key.strip())

        return self.success('Now try login here using a private key from the pair')


    

    def prepare_folder(self):
        ssh = self.normalize_path('~/.ssh')
        
        if not os.path.isdir(ssh):
            self.note('Creating ~/.ssh (%s), chmod 700' % ssh)
            
            os.mkdir(ssh, 0700)


