from robocorp.tasks import task
from robocorp import browser, http
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1000
    )
    orders = get_orders()
    page = browser.page()

    open_robot_order_website()

    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        pdf_file = store_receipt_as_pdf(order['Order number'])
        screenshot = screenshot_robot()
        embed_screenshot_to_receipt(screenshot, pdf_file, order)
        page.click('#order-another')
    
    archive_receipts()

def open_robot_order_website():
    browser.goto('https://robotsparebinindustries.com/#/robot-order')

def get_orders():
    csv_file = http.download('https://robotsparebinindustries.com/orders.csv', overwrite=True)
    library = Tables()

    orders = library.read_table_from_csv(
        csv_file,
        header=True
    )
    return orders

def close_annoying_modal():
    """Closes the annoying modal pop-up"""
    page = browser.page()
    page.click('.btn.btn-dark')

def fill_the_form(order):
    """Fills the form to order a robot"""
    page = browser.page()

    page.select_option('#head', value=order['Head'])
    page.click('#id-body-{}'.format(order['Body']))
    page.fill('.form-control', order['Legs'])
    page.fill('#address', order['Address'])
    page.click('#preview')
    page.click('#order')

    if page.is_visible('.alert.alert-danger'):
        while page.is_visible('.alert.alert-danger'):
            page.click('#order')

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator('#receipt').inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt, 'output/receipts/{}.pdf'.format(order_number))
    return pdf

def screenshot_robot():
    page = browser.page()
    screenshot = page.screenshot()
    return screenshot

def embed_screenshot_to_receipt(screenshot, pdf_file, order):
    screenshot_robot = open('screenshot.png', 'wb')
    screenshot_robot.write(screenshot)
    list_files = [
        f'output/receipts/{order["Order number"]}.pdf',
        f'screenshot.png:align=center'
    ]
    pdf_file.add_files_to_pdf(
        files=list_files,
        target_document=f'output/receipts/{order["Order number"]}.pdf'
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output/receipts', './output/receipts.zip', recursive=True)