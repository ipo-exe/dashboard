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
                                 'Descrip',
                                 'Status',
                                 'StartDate',
                                 'EndDate',
                                 'BackupDate',
                                 'Income',
                                 'Costs',
                                 'Net',
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


    def overwrite_dashboard_file(self):
        self.dashboard_df.to_csv(self.dashboard_fn, sep=';', index=False)


    def create_new_project(self, attr):
        """
        create a new project
        :param attr: dict of creation attributes:
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
        self.overwrite_dashboard_file()

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


    def update_project(self, attr):

        _p_id = attr['Id']
        _p_alias_old = self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], 'Alias'].values[0]
        print(_p_alias_old)
        _p_alias_new = attr['Alias']
        # change dir name
        if _p_alias_new != _p_alias_old:
            _scr = self.path + '/{}_{}'.format(_p_id, _p_alias_old)
            _dst = self.path + '/{}_{}'.format(_p_id, _p_alias_new)
            os.rename(src=_scr, dst=_dst)
        for k in attr:
            if k == 'Id':
                pass
            else:
                self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id'], k] = attr[k]
        self.overwrite_dashboard_file()

        #print(self.dashboard_df.loc[self.dashboard_df['Id'] == attr['Id']].to_string())

