import os
import shutil

import pandas as pd


class Hub:

    def __init__(self, root=".", name="myhub"):
        """
        initial method
        :param root: path to the root folder
        :type root: str
        :param name: hub name
        :type name: str
        """
        import os

        # get path
        self.name = name
        self.root = root
        self.path = root + "/" + name

        # get accounting path
        self.accounting_path = root + "/" + name + "/accounting"
        self.receipts_income_path = root + "/" + name + "/accounting/receipts_income"
        self.receipts_costs_path = root + "/" + name + "/accounting/receipts_costs"
        # define accounting dashboard filename
        self.accounting_fn = self.accounting_path + "/_accounting.txt"

        # get projects path
        self.projects_path = root + "/" + name + "/projects"
        self.templates_path = root + "/" + name + "/projects/templates"

        # define projects dashboard filename
        self.projects_fn = self.projects_path + "/_projects.txt"

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
            os.mkdir(self.receipts_income_path)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.receipts_costs_path)
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
            "Id",
            "TimeStamp",
            "Name",
            "Alias",
            "Kind",
            "ExpectTime",
            "ExpectNet",
            "ExpectYield",
            "Income",
            "Cost",
            "Net",
            "YieldMonth",
            "Status",
            "LclStatus",
            "DateStart",
            "DateEnd",
            "TimeRun",
            "DateBackup",
            "TimeBackup",
            "Description",
        ]
        # accounting attr
        self.accounting_attributes = [
            "Id",
            "TimeStamp",
            "ProjectId",
            "Kind",
            "Status",
            "ReceiptDate",
            "ReceiptValue",
            "ReceiptId",
            "ReceiptFile",
            "Description",
        ]

        # load dashboards

        # accounting dashboard
        if os.path.isfile(self.accounting_fn):
            self.accounting_df = pd.read_csv(
                self.accounting_fn, sep=";", parse_dates=["TimeStamp", "ReceiptDate"]
            )
        else:
            _df = pd.DataFrame(columns=self.accounting_attributes)
            _df.to_csv(self.accounting_fn, sep=";", index=False)
            self.accounting_df = pd.read_csv(
                self.accounting_fn, sep=";", parse_dates=["TimeStamp", "ReceiptDate"]
            )

        # projects dashboard
        if os.path.isfile(self.projects_fn):
            self.projects_df = pd.read_csv(
                self.projects_fn,
                sep=";",
                parse_dates=["DateStart", "DateEnd", "DateBackup"],
            )
        else:
            _df = pd.DataFrame(columns=self.project_attributes)
            _df.to_csv(self.projects_fn, sep=";", index=False)
            self.projects_df = pd.read_csv(
                self.projects_fn,
                sep=";",
                parse_dates=["DateStart", "DateEnd", "DateBackup"],
            )
        # refresh projects dashboard
        self.projects_refresh()

    def __str__(self):
        _s = (
            "Instance of Hub\n\n"
            "Projects dashboard:\n{}\n\n"
            "Accounting dashboard:\n{}".format(
                self.projects_df.to_string(), self.accounting_df.to_string()
            )
        )
        return _s

    def projects_overwrite(self):
        self.projects_df.to_csv(self.projects_fn, sep=";", index=False)

    def accounting_overwrite(self):
        self.accounting_df.to_csv(self.accounting_fn, sep=";", index=False)

    def projects_refresh(self, update_local=False):
        """
        refreshing operations on the projects dashboard
        :return:
        """
        # refresh expected yield
        for i in range(len(self.projects_df)):
            _months = pd.to_timedelta(self.projects_df["ExpectTime"].values[i]) / (
                    30 * pd.to_timedelta(1, unit="D"))
            self.projects_df["ExpectYield"].values[i] = self.projects_df["ExpectNet"].values[i] / _months

        # refresh Running time
        for i in range(len(self.projects_df)):
            if self.projects_df["DateEnd"].isna().values[i]:
                self.projects_df["TimeRun"].values[i] = pd.Timedelta(
                    pd.to_datetime("today") - self.projects_df["DateStart"].values[i]
                )
            else:
                self.projects_df["TimeRun"].values[i] = pd.Timedelta(
                    self.projects_df["DateEnd"].values[i]
                    - self.projects_df["DateStart"].values[i]
                )

        # refresh Backup time
        for i in range(len(self.projects_df)):
            if self.projects_df["DateBackup"].isna().values[i]:
                self.projects_df["TimeBackup"].values[i] = pd.Timedelta(
                    pd.to_datetime("today") - self.projects_df["DateStart"].values[i]
                )
            else:
                self.projects_df["TimeBackup"].values[i] = pd.Timedelta(
                    pd.to_datetime("today") - self.projects_df["DateBackup"].values[i]
                )

        # refresh income and costs
        for i in range(len(self.projects_df)):
            _lcl_id = self.projects_df['Id'].values[i]
            _df_acc = self.accounting_df.query("Status == 'executed'".format(_lcl_id))
            _df_acc = _df_acc.query("ProjectId == '{}'".format(_lcl_id))
            # income
            _df_acc_income = _df_acc.query("Kind == 'income'")
            self.projects_df["Income"].values[i] = _df_acc_income['ReceiptValue'].sum()
            # cost
            _df_acc_cost = _df_acc.query("Kind == 'cost'")
            self.projects_df["Cost"].values[i] = _df_acc_cost['ReceiptValue'].sum()

        # refresh balance
        self.projects_df["Net"] = self.projects_df["Income"] - self.projects_df["Cost"]
        self.projects_df.loc[self.projects_df["Cost"].isna(), "Net"] = self.projects_df[
            "Income"
        ]
        self.projects_df.loc[self.projects_df["Income"].isna(), "Net"] = (
            0.0 - self.projects_df["Cost"]
        )

        # refresh yield:
        for i in range(len(self.projects_df)):
            if self.projects_df["Net"].isna().values[i]:
                self.projects_df["YieldMonth"].values[i] = 0.0
            else:
                _months = self.projects_df["TimeRun"].values[i] / (
                    30 * pd.to_timedelta(1, unit="D")
                )
                self.projects_df["YieldMonth"].values[i] = (
                    self.projects_df["Net"].values[i] / _months
                )
        # update local status and project metadata
        if update_local:
            self.projects_df["LclStatus"] = ""
            for i in range(len(self.projects_df)):
                lcl_dir = "{}/{}_{}".format(
                    self.projects_path,
                    self.projects_df["Id"].values[i],
                    self.projects_df["Alias"].values[i],
                )
                if os.path.isdir(lcl_dir):
                    # set status
                    self.projects_df["LclStatus"].values[i] = "available"
                    # refresh local file
                    self.project_refresh(
                        attr={
                            "Id": self.projects_df["Id"].values[i],
                            "Alias": self.projects_df["Alias"].values[i],
                        }
                    )
                else:
                    # set status
                    self.projects_df["LclStatus"].values[i] = "unavailable"
        # overwrite file
        self.projects_overwrite()

    def project_create_new(self, attr):
        """
        create a new project
        :param attr: dict of creation attributes. must have:
        {
         'Name': '',
         'Alias': '',
         'Kind': '',
         'Description': ''
         'DateStart': ''
         }
        :return:
        """

        def stringfy(n):
            n = int(n)
            return "P{}".format(str(n).zfill(3))

        # get id
        p_id = stringfy(len(self.projects_df) + 1)
        attr["Id"] = p_id

        # get start date
        attr["TimeStamp"] = pd.to_datetime("today")
        attr["DateStart"] = pd.to_datetime(attr["DateStart"])

        # get status
        attr["Status"] = "on going"

        # bult dataframe
        _new_dct = dict()
        for k in attr:
            _new_dct[k] = [attr[k]]
        _new_df = pd.DataFrame(_new_dct)

        # insert project into dashboard
        self.projects_df = pd.concat(
            [self.projects_df, _new_df], ignore_index=True, axis=0
        )
        self.projects_overwrite()

        # create sub directories
        try:
            os.mkdir(self.projects_path + "/{}_{}".format(p_id, attr["Alias"]))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.projects_path + "/{}_{}/contract".format(p_id, attr["Alias"]))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.projects_path + "/{}_{}/inputs".format(p_id, attr["Alias"]))
        except FileExistsError:
            pass
        try:
            os.mkdir(self.projects_path + "/{}_{}/output".format(p_id, attr["Alias"]))
        except FileExistsError:
            pass

        # create project file
        self.project_refresh(attr=attr)
        # refresh projects dashboard
        self.projects_refresh()

        return attr

    def project_get_metadata(self, attr):
        """
        Return the metadata of a project
        :param attr: dict with the Id field
        :type attr: dict
        :return: dict of project metadata
        :rtype: dict
        """
        lcl_dct = dict()
        for k in self.project_attributes:
            lcl_dct[k] = self.projects_df.loc[
                self.projects_df["Id"] == attr["Id"], k
            ].values[0]
        return lcl_dct

    def projects_update(self, attr):
        """
        Void method to update a project data in the projects dashboard dataframe
        :param attr: dict of project updated attributes - must have the 'Id' and 'Alias' field
        :type attr: dict
        :return: None
        :rtype: None
        """
        _p_id = attr["Id"]
        dash_attr = self.project_get_metadata(attr=attr)
        # change change project dir name
        if "Alias" in attr.keys():
            # check if need to change project directory name
            if attr["Alias"] != dash_attr["Alias"]:
                _scr = self.path + "/{}_{}".format(_p_id, dash_attr["Alias"])
                _dst = self.path + "/{}_{}".format(_p_id, attr["Alias"])
                os.rename(src=_scr, dst=_dst)
        # update project dash
        for k in attr:
            if k == "Id":
                pass
            else:
                if k in set(self.project_attributes):
                    self.projects_df.loc[
                        self.projects_df["Id"] == attr["Id"], k
                    ] = attr[k]
        # refresh projects dataframe
        self.projects_refresh()
        # overwrite full file
        self.projects_overwrite()
        # overwrite local file
        self.project_refresh(attr=self.project_get_metadata(attr=attr))

    def project_refresh(self, attr):
        """
        refresh a project metadata file
        :param attr: dict of project attributes - must have the 'Id' and 'Alias' field
        :type attr: dict
        :return: None
        :rtype: None
        """
        _aux_df = self.projects_df.query('Id == "{}"'.format(attr["Id"]))
        s_dst = self.projects_path + "/{}_{}/metadata.txt".format(
            attr["Id"], attr["Alias"]
        )
        _aux_df.to_csv(s_dst, sep=";", index=False)

    def project_terminate(self, attr):
        """
        terminate a project in the project dashboard dataframe
        :param attr: dict of project updated attributes - must have the 'Id' field
        :return:
        """
        # set
        _attr = self.project_get_metadata(attr=attr)
        _attr["DateEnd"] = pd.to_datetime("today")
        _attr["Status"] = "terminated"
        self.projects_update(attr=_attr)
        self.projects_refresh()

    def project_backup(self, attr, dst):
        """
        backup project to destiny folder
        :param attr: dict of project attributes with 'Id' field to back up
        :type attr: dict
        :param dst: destination folder
        :type dst: str
        :return: none
        :rtype: none
        """
        from shutil import make_archive

        # set End date
        p_end = pd.to_datetime("today")
        self.projects_df.loc[self.projects_df["Id"] == attr["Id"], "DateBackup"] = p_end
        self.projects_refresh()
        self.projects_overwrite()
        # export zip file
        p_id = self.projects_df.loc[self.projects_df["Id"] == attr["Id"], "Id"].values[
            0
        ]
        p_alias = self.projects_df.loc[
            self.projects_df["Id"] == attr["Id"], "Alias"
        ].values[0]

        make_archive(
            base_name="{}/{}_{}_{}".format(
                dst, p_id, p_alias, p_end.strftime("%Y-%m-%d")
            ),
            format="zip",
            root_dir="{}/projects/{}_{}".format(self.path, p_id, p_alias),
        )
    
    def get_projects_summary(self):
        lst_summary = [
            'Id',
            'Status', 
            'Alias', 
            'Kind', 
            'ExpectTime', 
            'TimeRun', 
            'ExpectNet', 
            'Net', 
            'DateBackup'
        ]
        return self.projects_df[lst_summary].copy()
        
    def get_acc_summary(self):
        lst_summary_acc = [
            'Id', 
            'ProjectId', 
            'Kind',
            'Status', 
            'ReceiptDate', 
            'ReceiptValue', 
            'ReceiptId', 
            'Description', 
            'ReceiptFile'
        ]
        a_df = self.accounting_df[lst_summary_acc].copy()
        return a_df.sort_values(by='ReceiptDate', ascending=False)

    def get_acc_monthly_summary(self):
        aex_df = self.get_acc_summary().query("Status == 'executed'")
        # split
        a_incom_df = aex_df.query("Kind == 'income'").copy()
        a_costs_df = aex_df.query("Kind == 'cost'").copy()
        a_costs_df['ReceiptValue'] = - 1.0 * a_costs_df['ReceiptValue'].values
        # concat again
        aex_fix_df = pd.concat(
            [a_incom_df, a_costs_df], ignore_index=True
        )
        am_df = aex_fix_df[['ReceiptDate', 'ReceiptValue']].resample('MS', on='ReceiptDate').sum()
        am_df = am_df.fillna(0)
        return am_df.reset_index()
    
    def accounting_entry(self, attr):
        """
        Accounting entry protocol
        :param attr: dict of accounting entry
        :type attr: dict
        :return: none
        :rtype: none
        """
        # set entry id
        attr["Id"] = "A{}".format(str(len(self.accounting_df) + 1).zfill(3))
        # set entry date
        attr["TimeStamp"] = pd.to_datetime("today")
        attr["ReceiptDate"] = pd.to_datetime(attr["ReceiptDate"])

        # deploy new entry dataframe
        _df = pd.DataFrame(attr, index=[0])
        _df["ReceiptFile"] = ""

        # receipt file protocol
        _dct = self.project_get_metadata(attr={"Id": attr["ProjectId"]})  # get project metadata
        if os.path.isfile(path=attr["ReceiptFile"]):
            _extension = attr["ReceiptFile"].split(".")[-1]
            # copy file to accounting folder
            if attr['Kind'].lower() == "income":
                _dst_dir = self.receipts_income_path
            else:
                _dst_dir = self.receipts_costs_path
            _dst_fn = "{}_{}__{}_{}.{}".format(
                _dct["Id"], _dct["Alias"], attr["Id"], attr["ReceiptId"], _extension
            )
            _dst_file = "{}/{}".format(_dst_dir, _dst_fn)
            shutil.copy(src=attr["ReceiptFile"], dst=_dst_file)

            # copy file to project folder
            _dst_dir = "{}/{}_{}/contract".format(self.projects_path, _dct["Id"], _dct["Alias"])
            _dst_file = "{}/{}".format(_dst_dir, _dst_fn)
            shutil.copy(src=attr["ReceiptFile"], dst=_dst_file)
            # set
            _df["ReceiptFile"] = _dst_fn

        # append dataframe
        self.accounting_df = pd.concat(
            [self.accounting_df, _df], ignore_index=True
        )
        # filter
        self.accounting_df = self.accounting_df[self.accounting_attributes]
        # save
        self.accounting_overwrite()
        # refresh projects
        self.projects_refresh()

    def accounting_update(self, attr):
        # update accounting dataframe
        for k in attr:
            if k == "Id" or k == "ReceiptFile":
                pass
            else:
                if k in set(self.accounting_attributes):
                    self.accounting_df.loc[self.accounting_df["Id"] == attr["Id"], k] = attr[k]
        # update file
        for k in attr:
            if k == "ReceiptFile":
                # find project Id and kind
                _project_id = self.accounting_df.query("Id == '{}'".format(attr["Id"]))["ProjectId"].values[0]
                _key = self.accounting_df.query("Id == '{}'".format(attr["Id"]))["Kind"].values[0]
                # receipt file protocol
                _dct = self.project_get_metadata(attr={"Id": _project_id})  # get project metadata
                if os.path.isfile(path=attr["ReceiptFile"]):
                    _extension = attr["ReceiptFile"].split(".")[-1]
                    # copy file to accounting folder
                    if _key.lower() == "income":
                        _dst_dir = self.receipts_income_path
                    else:
                        _dst_dir = self.receipts_costs_path
                    _dst_fn = "{}_{}__{}_{}.{}".format(
                        _dct["Id"], _dct["Alias"], attr["Id"], attr["ReceiptId"], _extension
                    )
                    _dst_file = "{}/{}".format(_dst_dir, _dst_fn)
                    shutil.copy(src=attr["ReceiptFile"], dst=_dst_file)

                    # copy file to project folder
                    _dst_dir = "{}/{}_{}/contract".format(self.projects_path, _dct["Id"], _dct["Alias"])
                    _dst_file = "{}/{}".format(_dst_dir, _dst_fn)
                    shutil.copy(src=attr["ReceiptFile"], dst=_dst_file)
                    # set
                    self.accounting_df.loc[self.accounting_df["Id"] == attr["Id"], k] = _dst_fn
        # save
        self.accounting_overwrite()
        # refresh
        self.projects_refresh()