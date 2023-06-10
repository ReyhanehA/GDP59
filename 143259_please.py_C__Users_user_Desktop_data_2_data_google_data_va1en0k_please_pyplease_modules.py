import os
import ConfigParser

from pyplease import modules


class Module(modules.Module):
    """Please configurator"""

    @modules.action
    def add(self, values):
        """adds/edits a module for Please"""
        
        config = self.get_config()
        
        module_name = self.get_module_name(values)
        
        self.extra_params(values[1:])
            
        try:
            path = config.get('modules', module_name)
        except Exception:
            path = None

        path = self.ask('Path to the module?', path)

        self.register(module_name, path)

        self.success('Registered "%s" as "%s"' % (module_name, path))

    @modules.action
    def remove(self, values):
        """removes a module from Please"""
        config = self.get_config()
        
        module_name = self.get_module_name(values)

        self.extra_params(values[1:])
    
        try:
            path = config.get('modules', module_name)
        except Exception:
            self.failure("Can't find module '%s' in the config '%s'"
                         % (module_name, self.config_path))
            return

        config.remove_option('modules', module_name)

        config.write(open(self.config_path, 'wb'))

        self.success('Removed "%s" from "%s"' % (module_name, path))

    @modules.action('[-a]',
                    'registers default modules (-a to register all without asking)')
    def defaults(self, values):
        install_all = False
        
        if values and values[0] == '-a':
            values = values[1:]
            install_all = True

        self.extra_params(values)

        if install_all:
            self.warn('Going to register *all* default modules '
                      'without asking for your permission!')

        self.get_config() # before everything

        for module_name, path in modules.DEFAULTS:
            install = install_all or self.confirm('Install "%s"?' % module_name)

            if install:
                self.register(module_name, path)
                self.success('Registered "%s"' % module_name)

    @modules.action('[disable]', 'enables/disables autocompetion (if you have bash-autocomplete)')
    def autocomplete(self, values):
        cmd = """complete -C 'please --complete "$COMP_LINE"' please || true"""

        bashrc = self.ask('Path to the bashrc file?', '~/.bashrc')

        bashrc = self.normalize_path(bashrc)

        self.note('Using "%s" as bashrc' % bashrc)

        disable = False
        
        if values and values[0] == 'disable':
            values = values[1:]
            disable = True

        self.extra_params(values)

        if not disable:
        
            if self.has_line(bashrc, cmd):
                self.failure('Autocomplete seems already enabled')
                return
        
            self.backup(bashrc)
            
            self.append(bashrc, "\n%s\n\n" % cmd)

            self.success('Autocomplete enabled! Please re-login or use `source ~/.bashrc`')

            return

        else:
            self.backup(bashrc)

            lines = [l for l in open(bashrc) if l.strip() != cmd]

            f = open(bashrc, 'w')
            for l in lines:
                f.write(l)
            f.close()

            self.success('Autocomplete disabled!')

    @modules.action
    def configure(self, values):
        """configures everything: default modules and autocompletion"""
        
        self.defaults([])
        self.autocomplete([])
        

    def register(self, module_name, path):
        config = self.get_config()
        
        self.backup(self.config_path)

        if not config.has_section('modules'):
            config.add_section('modules')

        config.set('modules', module_name, path)

        config.write(open(self.config_path, 'wb'))
        
                
    def get_module_name(self, values):
        if values:
            return values[0]
        else:
            return self.ask('Module name?')
        
    
    def get_config(self):
        try:
            return self.config
        except AttributeError:
            pass

        self.config = ConfigParser.ConfigParser()
        
        path = self.ask('Path to the config?', '~/.pyplease')

        path = self.normalize_path(path)

        self.note('Using "%s" as config' % path)

        self.config.read([path])
        self.config_path = path

        return self.config
