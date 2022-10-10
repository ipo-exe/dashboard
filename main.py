import os
import pandas as pd


class Hub():

    def __init__(self, root='.', name='myhub'):
        import os

        # get path
        self.name = name
        self.root = root
        self.path = root + '/' + name

        # get accounting path
        self.accounting_path = root + '/' + name + '/accounting'
        self.receipts_path = root + '/' + name + '/accounting/receipts'
        # define accounting dashboard filename
        self.accouting_fn = self.accounting_path + '/_accounting.txt'

        # get projects path
        self.projects_path = root + '/' + name + '/projects'
        self.templates_path = root + '/' + name + '/projects/templates'

        # define projects dashboard filename
        self.projects_fn = self.projects_path + '/_projects.txt'

        # create directories
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.accounting_path)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.receipts_path)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.projects_path)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.templates_path)
        except FileExistsError:
            pass

        # set attributes dashboard

        # projects attr
        self.project_attributes = [
            'Id',
            'Name',
            'Alias',
            'Kind',
            'Status',
            'StartDate',
            'EndDate',
            'WorkingDays',
            'LastBackupDate',
            'NoBackupDays',
            'Income',
            'Costs',
            'Net',
            'Descrip',
            'LocalStatus'
        ]
        # accounting attr
        self.accouting_attributes = [
            'Date',
            'Value',
            'ProjectId',
            'ReceiptId',
            'ExternalId',
            'Descrip'
        ]

        # load dashboards

        # accounting dashboard
        if os.path.isfile(self.accouting_fn):
            self.accouting_df = pd.read_csv(self.accouting_fn, sep=';')
        else:
            self.accounting_create_dashboard()
            self.accouting_df = pd.read_csv(self.accouting_fn, sep=';')

        # projects dashboard
        if os.path.isfile(self.projects_fn):
            self.projects_df = pd.read_csv(
                self.projects_fn,
                sep=';',
                parse_dates=['StartDate', 'EndDate', 'LastBackupDate'])
        else:
            self.projects_create_dashboard()
            self.projects_df = pd.read_csv(
                self.projects_fn,
                sep=';',
                parse_dates=['StartDate', 'EndDate', 'LastBackupDate'])

    def __str__(self):
        _s = "Instance of Hub\n{}".format(self.projects_df.to_string())
        return _s

    def projects_create_dashboard(self):
        _df = pd.DataFrame(columns=self.project_attributes)
        _df.to_csv(self.projects_fn, sep=';', index=False)

    def accounting_create_dashboard(self):
        _df = pd.DataFrame(columns=self.accouting_attributes)
        _df.to_csv(self.accouting_fn, sep=';', index=False)

    def projects_overwrite(self):
        self.projects_df.to_csv(self.projects_fn, sep=';', index=False)

    def projects_refresh(self):
        """
        refreshing operations on the projects dashboard
        :return:
        """
        from datetime import date
        # refresh accounting
        self.projects_df['Net'] = self.projects_df['Income'] - self.projects_df['Costs']

        self.projects_df['WorkingDays'] = self.projects_df['EndDate'] - self.projects_df['StartDate']
        self.projects_df['NoBackupDays'] = date.today() - self.projects_df['LastBackupDate']
        print(self.projects_df['WorkingDays'].dtype)
        print(self.projects_df['NoBackupDays'].dtype)
        self.projects_overwrite()

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
            return 'P{}'.format(str(n).zfill(3))

        # get id
        p_id = stringfy(len(self.projects_df) + 1)
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
        self.projects_df = pd.concat([self.projects_df, _new_df], ignore_index=True, axis=0)
        self.projects_overwrite()

        # create sub directories
        try:
            os.mkdir(self.projects_path + '/{}_{}'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.projects_path + '/{}_{}/contract'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.projects_path + '/{}_{}/inputs'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.projects_path + '/{}_{}/output'.format(p_id, attr['Alias']))
        except FileExistsError:
            pass

        # create project file
        self.project_refresh(attr=attr)
        # refresh projects dashboard
        self.projects_refresh()

        return attr

    def project_get_metadata(self, attr):
        lcl_dct = dict()
        for k in self.project_attributes:
            lcl_dct[k] = self.projects_df.loc[self.projects_df['Id'] == attr['Id'], k].values[0]
        return lcl_dct

    def project_update_meta(self, attr):
        '''
        update a project metadata in the project dashboard dataframe
        :param attr: dict of project updated attributes - must have the 'Id' and 'Alias' field
        :return:
        '''

        _p_id = attr['Id']
        dash_attr = self.project_get_metadata(attr=attr)
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
                    self.projects_df.loc[self.projects_df['Id'] == attr['Id'], k] = attr[k]
        self.projects_refresh()
        self.projects_overwrite()
        self.project_refresh(attr=attr)


    def project_refresh(self, attr):
        _aux_df = self.projects_df.query('Id == "{}"'.format(attr['Id']))
        s_dst = self.projects_path + '/{}_{}/metadata.txt'.format(attr['Id'], attr['Alias'])
        _aux_df.to_csv(s_dst, sep=';', index=False)

    def project_terminate(self, attr):
        '''
        terminate a project in the project dashboard dataframe
        :param attr: dict of project updated attributes - must have the 'Id' field
        :return:
        '''
        from datetime import date
        # get start date
        today = date.today()
        # set
        _attr = self.project_get_metadata(attr=attr)
        _attr['EndDate'] = today.strftime("%Y-%m-%d")
        _attr['Status'] = 'terminated'
        self.project_update_meta(attr=_attr)


    def project_backup(self, attr, dst):
        """
        backup project to destiny folder
        :param attr: dict of project attributes with 'Id' field to back up
        :param dst:
        :return:
        """
        from shutil import make_archive
        from datetime import date
        # get start date
        today = date.today()
        # set End date
        p_end = today.strftime("%Y-%m-%d")
        self.projects_df.loc[self.projects_df['Id'] == attr['Id'], 'BackupDate'] = p_end
        self.projects_refresh()
        self.projects_overwrite()
        # export zip file
        p_id = self.projects_df.loc[self.projects_df['Id'] == attr['Id'], 'Id'].values[0]
        p_alias = self.projects_df.loc[self.projects_df['Id'] == attr['Id'], 'Alias'].values[0]
        #make_archive('{}_{}_{}'.format(p_id, p_alias, p_end), 'zip', dst)

        make_archive(base_name='{}/{}_{}_{}'.format(dst, p_id, p_alias, p_end),
                     format='zip',
                     root_dir='{}/{}_{}'.format(self.path, p_id, p_alias))

    def project_inspect(self, attr):
        pass
