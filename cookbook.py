

def void_open_hub():
    from main import Hub

    # open/create hub
    myhub = Hub(root='C:/bin', name='hub1')
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
    myhub = Hub(root='C:/bin', name='hub1')

    # update form
    myhub.accounting_entry(
        attr={
            "ProjectId": "P001",
            "Kind": "Income",
            "ExpectedValue": 2000,
            "ReceiptDate": "2022-10-05",
            "ReceiptValue": 2000,
            "ReceiptFile": "C:/Users/Ipo/Desktop/johnson-laird2010.pdf",
            "ReceiptId": "R0003",
            "Description": "Payment of services"
        }
    )
    print(myhub)

if __name__ == "__main__":
    print('hi')
    void_entry_account()