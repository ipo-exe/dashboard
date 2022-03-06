import os
import pandas as pd


class Hub():

    def __init__(self, root='.', name='myhub'):
        import os
        # get path
        self.path = root + '/' + name
        # define dashboard filename
        self.dashboard_fn = self.path + '/dashboard.txt'
        # instantiate dataframe
        self.project_attributes = ['Id',
                                   'Name',
                                   'Alias',
                                   'Kind',
                                   'Status',
                                   'StartDate',
                                   'EndDate',
                                   'BackupDate',
                                   'Income',
                                   'Costs',
                                   'Net',
                                   'Descrip',
                                   'Log']
        self.dashboard_df = pd.DataFrame(columns=self.project_attributes)
        if os.path.isdir(self.path):
            # dir already exists
            if os.path.isfile(self.dashboard_fn):
                # load dataframe from file
                _aux_df = pd.read_csv(self.dashboard_fn, sep=';')
                for f in self.project_attributes:
                    if f in set(_aux_df.columns):
                        self.dashboard_df[f] = _aux_df[f].values
                    else:
                        self.dashboard_df[f] = ''
            # re-write dashboard csv file
            self.dashboard_df.to_csv(self.dashboard_fn, sep=';', index=False)
        else:
            # create directory
            os.mkdir(self.path)
            # create dashboard csv file
            self.dashboard_df.to_csv(self.dashboard_fn, sep=';', index=False)


    def dashboard_overwrite(self):
        self.dashboard_df.to_csv(self.dashboard_fn, sep=';', index=False)


    def dashboard_refresh(self):
        self.dashboard_df['Net'] = self.dashboard_df['Income'] - self.dashboard_df['Costs']


    def project_create_new(self, attr):
        """
        create a new project
        :param attr: dict of creation attributes. must have:
        {'Name': '', 'Alias': '', 'Kind': '', 'Descrip.': ''}
        :return:
        """
        from datetime import date

        def stringfy(n):
            n = int(n)
            if n < 10:
                return 'P00{}'.format(n)
            elif n >= 10 and n < 100:
                return 'P0{}'.format(n)
            else:
                return 'P{}'.format(n)

        # get id
        p_id = stringfy(len(self.dashboard_df))
        attr['Id'] = p_id

        # get start date
        today = date.today()
        attr['StartDate'] = today.strftime("%Y-%m-%d")

        # get status
        attr['Status'] = 'on going'

        # bult dataframe
        _new_dct = dict()
        for k in attr:
            _new_dct[k] = [attr[k]]
        _new_df = pd.DataFrame(_new_dct)

        # insert project into dashboard
        self.dashboard_df = pd.concat([self.dashboard_df, _new_df], ignore_index=True, axis=0)
        self.dashboard_overwrite()

        # create sub directories
        try:
            os.mkdir(self.path + '/{}_{}'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.path + '/{}_{}/contract'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.path + '/{}_{}/inputs'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.path + '/{}_{}/output'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass


    def project_update_meta(self, attr):
        '''
        update a project metadata in the dashboard dataframe
        :param attr: dict of project updated attributes - must have the 'Id' and 'Alias' field
        :return:
        '''

        def project_get_metadata(attr):
            lcl_dct = dict()
            for k in self.project_attributes:
                lcl_dct[k] = self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], k].values[0]
            return lcl_dct

        _p_id = attr['Id']
        dash_attr = project_get_metadata(attr=attr)
        # change change project dir name
        if attr['Alias'] != dash_attr['Alias']:
            _scr = self.path + '/{}_{}'.format(_p_id, dash_attr['Alias'])
            _dst = self.path + '/{}_{}'.format(_p_id, attr['Alias'])
            os.rename(src=_scr, dst=_dst)
        for k in attr:
            if k == 'Id':
                pass
            else:
                if k in set(self.project_attributes):
                    self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], k] = attr[k]
        self.dashboard_refresh()
        self.dashboard_overwrite()


    def project_terminate(self, attr):
        '''
        terminate a project in the dashboard dataframe
        :param attr: dict of project updated attributes - must have the 'Id' field
        :return:
        '''
        from datetime import date
        # get start date
        today = date.today()
        # set Status
        self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], 'Status'] = 'terminated'
        # set End date
        self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], 'EndDate'] = today.strftime("%Y-%m-%d")
        self.dashboard_refresh()
        self.dashboard_overwrite()


    def project_backup(self, attr, dst):
        from shutil import make_archive
        from datetime import date
        # get start date
        today = date.today()
        # set End date
        p_end = today.strftime("%Y-%m-%d")
        self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], 'BackupDate'] = p_end
        self.dashboard_refresh()
        self.dashboard_overwrite()
        # export zip file
        p_id = self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], 'Id'].values[0]
        p_alias = self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], 'Alias'].values[0]
        #make_archive('{}_{}_{}'.format(p_id, p_alias, p_end), 'zip', dst)

        make_archive(base_name='{}/{}_{}_{}'.format(dst, p_id, p_alias, p_end),
                     format='zip',
                     root_dir='{}/{}_{}'.format(self.path, p_id, p_alias))

    def project_inspect(self, attr):
        pass
