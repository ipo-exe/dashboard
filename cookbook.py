

def void_open_hub():
    from main import Hub

    # open/create hub
    myhub = Hub(root='C:/000_myFiles/myDrive', name='hub01')
    print(myhub)


def void_create_project():
    from main import Hub

    # open hub
    myhub = Hub(root='C:/bin', name='hub1')

    # fill form
    myhub.project_create_new(
        attr={
            "Name": "ProjectB",
            "Alias": "pB",
            "Kind": "consulting",
            "Description": "A consulting project",
            "DateStart": "2022-10-20",
            "ExpectNet": 30000,
            "ExpectTime": "180 days"
        }
    )
    print(myhub)


def void_update_project():
    from main import Hub

    # open hub
    myhub = Hub(root='C:/bin', name='hub2')

    # update form
    myhub.projects_update(
        attr={
            "Id": "P001",
            "Alias": "p1",
            "Kind": "extension",
            "Description": "An extension project"
        }
    )
    print(myhub)


def void_entry_account():
    from main import Hub

    # open hub
    myhub = Hub(root='C:/000_myFiles/myDrive', name='hub01')

    # update form
    myhub.accounting_entry(
        attr={
            "ProjectId": "P001",
            "Kind": "Income",
            "Status": 1650,
            "ReceiptDate": "2022-11-07",
            "ReceiptValue": 1650,
            "ReceiptFile": r"C:\000_myFiles\myDrive\hub01\projects\P001_teia-elera\contract\NF2022-11_parcela2.pdf",
            "ReceiptId": "NF2022-11",
            "Description": "Service payments - parcel #2"
        }
    )
    print(myhub)

if __name__ == "__main__":
    print('hi')
    void_entry_account()