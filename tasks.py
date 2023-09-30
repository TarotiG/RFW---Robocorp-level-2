from robocorp.tasks import task
from robocorp import browser, http
from RPA.Tables import Tables
from RPA.PDF import PDF

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

    open_robot_order_website()

    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        store_receipt_as_pdf(order['Order number'])
        embed_screenshot_to_receipt(
            screenshot_robot(order['Order number']),
              f'./output/receipts/{order["Order number"]}.pdf')

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
    error_message = page.get_by_text(text='Internal Server Error')


    page.select_option('#head', value=order['Head'])
    page.click('#id-body-{}'.format(order['Body']))
    page.fill('.form-control', order['Legs'])
    page.fill('#address', order['Address'])
    page.click('#preview')
    page.click('#order')

    if error_message.is_visible():
        while error_message.is_visible():
            page.click('#order')

            if not error_message.is_visible():
                break

def store_receipt_as_pdf(order_number):
    # robot-preview-image
    page = browser.page()
    receipt = page.locator('#receipt').inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt, 'output/receipts/{}.pdf'.format(order_number))

def screenshot_robot(order_number):
    # '#robot-preview-image'
    page = browser.page()
    return page.screenshot()

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf_file += screenshot

def archive_receipts():
    pass