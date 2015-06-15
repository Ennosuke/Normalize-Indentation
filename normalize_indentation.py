import sublime, sublime_plugin, time

class NormalizeIndentationCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Starting to normalize indentation')
        global_settings = sublime.load_settings('Preferences.sublime-settings') #First get global settings
        syntax = self.view.settings().get('syntax') #next we need the syntax settings
        segments = syntax.split('/')
        language = ''
        for segment in segments:
            if (segment.endswith('.tmLanguage')):
                language = segment.replace('.tmLanguage', '')
        syntax_settings = sublime.load_settings(language+'.sublime-settings')
        wanted_tabsize = global_settings.get('tab_size') #use the global settings later we overwrite it with syntax settings if there are any
        translate_tabs_to_spaces = global_settings.get('translate_tabs_to_spaces');
        if(syntax_settings):
            if(syntax_settings.get('tab_size')):
                wanted_tabsize = syntax_settings.get('tab_size')
            if(syntax_settings.get('translate_tabs_to_spaces')):
                translate_tabs_to_spaces = syntax_settings.get('translate_tabs_to_spaces')
        self.view.run_command('detect_indentation') #get the current indentation state
        view_tabsize = self.view.settings().get('tab_size')
        view_translate_tabs_to_spaces = self.view.settings().get('translate_tabs_to_spaces')
        if (translate_tabs_to_spaces == False): #we want tabs and don't care what the current state is
            print('converting spaces to tabs')
            self.view.run_command('unexpand_tabs')
            self.view.settings().set('tab_size', wanted_tabsize)
            region = sublime.Region(0, self.view.size())
            self.view.sel().add(region)
            self.view.run_command('reindent')
            self.view.sel().subtract(region)
        elif (view_translate_tabs_to_spaces == False and translate_tabs_to_spaces == True and view_tabsize == wanted_tabsize): #we have tabs but want spaces
            print('converting tabs to spaces')
            region = sublime.Region(0, self.view.size())
            self.view.sel().add(region)
            self.view.run_command('reindent')
            self.view.sel().subtract(region)
            self.view.run_command('expand_tabs')
            self.view.settings().set('translate_tabs_to_spaces', True)
        elif (view_translate_tabs_to_spaces == True and view_tabsize != wanted_tabsize): #we have spaces but the tab_size does not fit
            print('setting right tabsize')
            self.view.run_command('unexpand_tabs') #first convert to tabs
            self.view.settings().set('tab_size', wanted_tabsize) # change size
            self.view.run_command('expand_tabs') #expand again
            self.view.settings().set('translate_tabs_to_spaces', True)
            region = sublime.Region(0, self.view.size())
            self.view.sel().add(region)
            self.view.run_command('reindent')
            self.view.sel().subtract(region)
        else:
            print('all is fine and dandy')
        print('Done normalizing indentation')

        sublime.status_message('Done normalizing indentation')
class NormalizeIndentationOnOpen(sublime_plugin.EventListener):
    def on_load(self, view):
        settings = sublime.load_settings('Normalize Indentation.sublime-settings')
        if(settings.get('convert_on_open', True)): #only run if the user wants it, default value is False
            view.run_command('normalize_indentation')
    def on_activated(self, view): #run when view gains editing focus
        settings = sublime.load_settings('Normalize Indentation.sublime-settings')
        if(settings.get('convert_on_activate', True)):
            view.run_command('normalize_indentation')
