from datetime import datetime
import pyautogui
from time import *
from PIL import Image, ImageGrab
import random
import string
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
accounts_url = "https://roiefiz.pythonanywhere.com/accounts"
my_own_macbook_locations = {'travel_img_location': (207.0, 183),
                            'go_to_terravilla_button_location': (716.0, 305.4246861924686),
                            'infiniportal_location': (1039.0, 457.04288702928864),
                            'infiniportal_input_box': (825.0, 450.7133891213389),
                            'store_search_box': (610.0, 380.9623430962343),
                            'store_sell_tab_location': (1033.0, 325.6276150627615),
                            'buy_max_button_location': (917.9999999999999, 636.0878661087866),
                            'buy_input_quantity_location': (772.9999999999999, 625.3619246861924),
                            'confirm_buy_location': (740.0, 750.0669456066945),
                            'sell_max_button_location': (917.9999999999999, 655.0878661087866),
                            'sell_input_quantity_location': (817, 667),
                            'confirm_sell_location': (740.0, 770.0669456066945),
                            'log_out_button_location': (1437.0, 340.8661087866109),
                            'profile_clicked_by_mistake': (989.0, 200.91736401673637),
                            'large_map_button': (32.999999999999996, 343.8661087866109),
                            'land_number_sign_location': (1000, 400),
                            'star_icon_location': (187, 256),
                            "inventory_first_location": (512, 666),
                            "inventory_second_location": (596, 671),
                            "inventory_seventh_location": (516, 751),
                            "tutorial_username_input": (747, 502),  # can also be the first input element with selenium
                            "tutorial_continue_button": (741, 549),  # can also be the first button element
                            "tutorial_mark_understand_terms": (337, 800),  # can also be the first input
                            "tutorial_accept_button": (1080, 805),  # can also be the first button element
                            "tutorial_barney_location": (950, 506),
                            "tutorial_field_location": (800, 435),
                            "tutorial_figure_location": (810, 533),
                            "tutorial_ranger_location": (623, 545),
                            "tutorial_hazel_location": (1080, 400)
                            }


locations_script = "scaled_locations = {key: (value[0] - 55, value[1] - 60) for key, value in scaled_locations.items()}"


def generate_random_username():
    # Combine digits and letters
    characters = string.digits + string.ascii_letters

    # Generate a random string of length 6
    random_string = ''.join(random.choice(characters) for _ in range(7)).lower()

    return random_string


def keyboard_move_figure(direction: str, duration: float):
    pyautogui.keyDown(direction)
    sleep(duration)
    pyautogui.keyUp(direction)


class PixelsUser:
    def __init__(self, my_driver=None, operation_system='windows'):
        self.username = generate_random_username()
        self.email = self.username + '@mail7.io'
        self.software = 'windows'
        self.website = 'https://play.pixels.xyz'
        self.screen_width, self.screen_height = pyautogui.size()
        self.expected_size = (self.screen_width, self.screen_height)
        self.arranged_inventory = None
        self.errors_notifier = 0
        self.mail_for_errors = ["rfpb@mail7.io"]
        self.divide_by_screen_width = 1 / self.screen_width
        self.divide_by_screen_height = 1 / self.screen_height
        self.get_close_to_the_soil = 30
        self.quantity_input_highlight_distance = -30
        self.press_on_color_hold_duration = 0.7
        self.click_fields_offset = 65
        self.range_middle_x = (700, 900)
        self.range_middle_y = (500, 700)
        self.inventory_gap_x = 78
        self.inventory_gap_y = 81
        self.clicking_fields_dict = dict(up=(self.click_fields_offset * 1), down=(self.click_fields_offset * 2),
                                         right=(self.click_fields_offset * 1.5), left=(self.click_fields_offset * 1),
                                         costume=(30, 50))
        if operation_system == 'macOS':
            self.ctrl_keyboard = 'command'
            self.COLORS = {
                "center_color": (128, 186, 55),
                # fountain_color =  (181, 222, 69), (75, 114, 39), (123, 183, 54)
                "bucks_store_color": (67, 85, 138),
                "sell_desk_color": (143, 155, 155),
                "energy_yellow_color": (232, 254, 97),
                "ranger_farms_shop_color": (138, 154, 156),
                "infiniportal_red_machine": (161, 176, 170),
                "land_number_sign_color": (119, 69, 73),
                "empty_soil_color": (181, 131, 103),
                "worked_on_soil_color": (204, 160, 100),
                "land_sign_color": [(119, 69, 73), (118, 69, 73), (104, 57, 50)],
                "black_in_shop": (16, 16, 16),
                "Seeds_package": [(169, 151, 118), ],
                "dominant_colors": {
                    "Popberry": [(201, 232, 208), (207, 236, 210), (202, 232, 208), (135, 183, 186), (107, 162, 192),
                                 (100, 144, 189), (77, 122, 169)],
                    "Butterberry": [(245, 194, 78), (247, 234, 139), (227, 181, 85), (222, 175, 80), (245, 195)],
                    "Clover": [(57, 121, 33), (56, 118, 32), (29, 74, 34), (37, 86, 37), (61, 123, 34)],
                    "Grainbow": [(178, 61, 56), (184, 66, 56), (174, 61, 56), (177, 60, 56), (175, 61, 55)],
                    "purple_tickets": [(91, 45, 245), (90, 42, 247)],
                    "water_can": [(73, 29, 93), (117, 51, 44), (156, 166, 158)],
                    'shears': [(66, 93, 110), (39, 46, 78)]
                }
            }

        else:
            self.ctrl_keyboard = 'ctrl'
            self.COLORS = {
                "center_color": (122, 73, 250),
                "bucks_store_color": (60, 82, 139),
                "sell_desk_color": (240, 235, 198),
                "energy_yellow_color": (227, 255, 55),
                "ranger_farms_shop_color": (71, 65, 148),
                "infiniportal_red_machine": (158, 175, 169),
                "red_elephant": (255, 83, 193),
                "land_number_sign_color": (127, 66, 72),
                "empty_soil_color": (190, 128, 98),
                "worked_on_soil_color": (212, 158, 89),
                "land_sign_color": [(150, 95, 81), (112, 54, 48), (170, 119, 119), (112, 54, 48)],
                "black_in_shop": (16, 16, 16),
                "Seeds_package": [(173, 150, 113)],
                "dominant_colors": {
                    "Popberry": [(123, 188, 188), (199, 236, 208), (84, 142, 192), (124, 188, 188), (142, 189, 188)],
                    "Butterberry": [(245, 194, 78), (247, 234, 139), (227, 181, 85), (222, 175, 80), (245, 195)],
                    "Clover": [(57, 121, 33), (56, 118, 32), (29, 74, 34), (37, 86, 37), (61, 123, 34)],
                    "Grainbow": [(178, 61, 56), (184, 66, 56), (174, 61, 56), (177, 60, 56), (175, 61, 55)],
                    "purple_tickets": [(91, 45, 245), (90, 42, 247)],
                    "water_can": [(83, 28, 99), (117, 54, 100), (71, 114, 137), (215, 248, 237)],
                    'shears': [(228, 250, 243), (155, 184, 182), (229, 152, 146), (28, 37, 74)]
                }
            }

        if my_driver == "test":
            self.driver = "Testing, selenium not required"
            self.LOCATIONS = my_own_macbook_locations
            print(self.driver)
        elif my_driver is None:
            self.driver = webdriver.Chrome()
        else:
            self.driver = my_driver

    def initiate_new_account(self,first_time=False):
        with open('accounts.text','a') as accounts_text_file:
            accounts_text_file.write(f'{self.username}, {self.email} \n')
        self.driver.get('https://play.pixels.xyz')
        self.driver.maximize_window()
        sleep(5)
        log_in = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[3]/div[2]/div[1]/button[1]')
        log_in.click(), sleep(2)
        email_radio_xpath = '//*[@id="__next"]/div/div[3]/div[2]/div[1]/div[2]/div[1]/label[3]/input'
        email_radio = self.driver.find_element(By.XPATH, email_radio_xpath)
        email_radio.click(), sleep(2)
        email_input = self.driver.find_element(By.XPATH,
                                               '/html/body/div[1]/div/div[3]/div[2]/div[1]/div[2]/div[2]/input')
        email_input.send_keys(f'{self.email}'), sleep(3)
        pyautogui.press('enter')
        pyautogui.press('enter')
        sleep(5)
        create_new_account_button_xpath = '//*[@id="__next"]/div/div[3]/div[2]/div[1]/div[2]/button[1]'
        create_new_account_button = self.driver.find_element(By.XPATH, create_new_account_button_xpath)
        create_new_account_button.click()
        sleep(3)
        code = self.get_code_from_mail_7(mail7_mail=self.email)
        sleep(1)
        pyautogui.hotkey(self.ctrl_keyboard, "w")
        self.driver.switch_to.window(self.driver.window_handles[0]), sleep(1)
        pyautogui.typewrite(f'{code}')
        sleep(3)
        pyautogui.hotkey('enter')
        sleep(3)
        # enter username
        username_input = self.driver.find_element(By.TAG_NAME, 'input')
        username_input.send_keys(self.username)
        sleep(2)
        # continue button
        self.driver.find_element(By.TAG_NAME, 'button').click()
        sleep(3)
        # start game
        start_game_button = self.driver.find_element(By.XPATH,
                                                     '//*[@id="__next"]/div/div[3]/div[2]/button[1]')
        start_game_button.click()
        sleep(4)
        got_box = False
        trying_counter = 0
        while not got_box:
            try:
                self.driver.find_element(By.TAG_NAME, 'input').click()
            except NoSuchElementException:
                pass
            else:
                got_box = True
            finally:
                sleep(1)
                trying_counter += 1
                if trying_counter > 120:
                    raise Exception('Its too slow to initialize the account')
        accept_full_xpath_button = '/html/body/div[1]/div/div[3]/div/div[2]/div/div/button'  # button. 'Accept' in text.
        sleep(0.3)
        self.driver.find_element(By.XPATH, accept_full_xpath_button).click()
        sleep(3)
        barney_location = self.LOCATIONS["tutorial_barney_location"]
        self.skip_dialog()
        if first_time:
            for i in range(200):
                print("Get the next location.")
                input("Ready? ")
                sleep(5)
                print(pyautogui.position())
        sleep(5)
        pyautogui.click(barney_location[0], barney_location[1])
        sleep(1)
        self.skip_dialog()
        sleep(3)
        # plant the seed. seed at first location in inventory. field at 1142, 511
        field_location = self.LOCATIONS["tutorial_field_location"]
        pyautogui.hotkey('1')  # self.inventory_dic[1][0] == first inventory location
        sleep(0.3)
        pyautogui.click(field_location)
        sleep(0.3)
        # click on barney
        pyautogui.click(barney_location[0], barney_location[1])
        sleep(0.3)
        # skip dialog
        self.skip_dialog()
        sleep(0.3)
        # water the seed, pitcher on first location. bring the pitcher back in place
        pyautogui.hotkey('1')
        sleep(0.3)
        pyautogui.click(field_location)
        sleep(0.3)
        pyautogui.hotkey('1')
        sleep(0.2)
        # click on barney
        pyautogui.click(barney_location)
        # skip dialog
        sleep(0.3)
        self.skip_dialog()
        sleep(0.2)
        # fertilize the seed , fertilizer on the second position . bring the fertilizer back in place
        pyautogui.hotkey('2')
        sleep(0.2)
        pyautogui.click(field_location)
        sleep(0.2)
        pyautogui.hotkey('2')
        sleep(2)

        # click on barney
        pyautogui.click(barney_location)
        sleep(0.2)
        # skip dialog
        self.skip_dialog()
        sleep(0.2)
        # sheer the prospberry, the shovel on the 3rd place
        pyautogui.hotkey('2')
        sleep(0.2)
        pyautogui.click(field_location)
        sleep(0.2)
        pyautogui.hotkey('2')
        sleep(0.2)
        # click on barney
        pyautogui.click(barney_location)
        sleep(0.2)
        # skip dialog
        self.skip_dialog()
        sleep(0.2)
        # eat the Popberry
        pyautogui.hotkey('3')
        sleep(0.2)
        pyautogui.click(self.LOCATIONS["tutorial_figure_location"])
        sleep(0.2)
        # click on barney and skip dialog
        pyautogui.click(barney_location)
        sleep(0.2)
        self.skip_dialog()
        # sleep 12 - going to the farmer
        sleep(7)
        # skip dialog
        self.skip_dialog()
        sleep(0.1)
        # click on ranger dale
        self.skip_dialog()
        ranger_location = self.LOCATIONS["tutorial_ranger_location"]
        pyautogui.click(ranger_location)
        sleep(0.2)
        self.skip_dialog()
        sleep(2)
        # go to buck galore store
        self.go_to_hazels_counter()

    def find_pixels_with_color(self, image_path, target_color):
        self.errors_notifier = 1
        # Open the image
        img = Image.open(image_path).convert("RGB").resize(self.screen_width, self.screen_height)
        # Get the width and height of the image
        width, height = img.size

        # Create a list to store the coordinates of pixels with the target color
        matching_pixels = []

        # Iterate through each pixel in the image
        for x in range(width):
            for y in range(height):
                # Get the RGB values of the current pixel
                pixel_color = img.getpixel((x, y))

                # Check if the pixel color matches the target color
                if pixel_color == target_color:
                    matching_pixels.append((x, y))

        return matching_pixels

    def send_image_email(self, target_mail, body_text, image_path="problems.png"):
        self.errors_notifier = 2
        mail_to = target_mail
        my_email = "roied032@gmail.com"
        receive_mail = mail_to
        gmail_app_python_password = "jbvlmgjssnkqipqq"

        subject = "Message with Image"
        body = f"Error at M's bot {body_text}"

        # Create the MIMEMultipart object
        em = MIMEMultipart()
        em['From'] = my_email
        em['To'] = receive_mail
        em['Subject'] = subject

        # Attach the body as text
        em.attach(MIMEText(body, 'plain'))
        if bool(image_path):
            # Attach the image
            image_path = image_path
            with open(image_path, 'rb') as img_file:
                img = MIMEImage(img_file.read(), name="image.png")
                em.attach(img)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host='smtp.gmail.com', port=465, context=context) as connection:
            connection.login(user=my_email, password=gmail_app_python_password)
            connection.sendmail(from_addr=my_email, to_addrs=receive_mail, msg=em.as_string())

    def record_error(self, *args):
        self.errors_notifier = 3
        with open("errors.text", 'a') as errors_file:
            capture_error = ImageGrab.grab()
            capture_error.save('problems.png')
            errors_file.write(f'Problem screenshot at problems.png file \n {datetime.now()} {args}')
        for email in self.mail_for_errors:
            self.send_image_email(body_text=args, target_mail=email)

    def find_first_pixel(self, target_color, image=None, from_arrange=False, min_x=1, min_y=1, max_x=None, max_y=None):
        self.errors_notifier = 4
        print("Inside find first pixel function")
        if target_color == self.COLORS["energy_yellow_color"] or from_arrange:
            min_x = 0
        else:
            min_x = 100
        if image is None and from_arrange:
            return None
        elif image is None:
            image = ImageGrab.grab().convert(mode="RGB").resize(self.expected_size)
            image.save("screenshot.png")

        if bool(image):
            width, height = image.size
            if max_x is None:
                max_x = width - 2
            if max_y is None:
                max_y = height - 2

            for y in range(max_y):

                for x in range(max_x):
                    if x <= min_x or x > max_x:
                        continue
                    pixel = image.getpixel((x, y))
                    if pixel == target_color:
                        print(f"pixel found {target_color}")
                        return x, y

        # If the target color is not found, return None
        return None

    def press_on_color(self, target_color: tuple = (181, 211, 239)):
        self.errors_notifier = 5
        screenshot = ImageGrab.grab().convert("RGB").resize(self.expected_size)
        screenshot.save("screenshot.png")

        # Open an image
        image_path = "screenshot.png"  # Replace with the path to your image
        img = Image.open(image_path)

        # Find the location of the first pixel with the target color
        result = self.find_first_pixel(target_color, img)
        if result:
            print(f"Location of the first pixel with color {target_color}: {result}")
            # Specify the coordinates (x, y) where you want to click and hold
            x, y = result

            # Set the duration to click and hold (in seconds)
            hold_duration = self.press_on_color_hold_duration

            # Click and hold at the specified location
            pyautogui.mouseDown(x, y)

            # Sleep for the specified duration
            sleep(hold_duration)

            # Release the mouse click
            pyautogui.mouseUp(x, y)
            pos = (x, y)
            return pos
        else:
            print(f"No pixel found with color {target_color}")
            return False

    def make_sure_game_is_on(self):
        self.errors_notifier = 6
        counter = 0
        print('Making Sure The game is on ----')
        print(self.COLORS["energy_yellow_color"])
        while not bool(self.find_first_pixel(self.COLORS["energy_yellow_color"])):
            print('Game is still not on')
            sleep(1.5)
            counter += 1
            if counter >= 140:
                raise Exception("3 minutes passed without the game on")

    def discover_needed_operation(self):
        """

        :return: str, plant, water can or shears
        """
        self.errors_notifier = 8
        empty_field = self.find_first_pixel(target_color=self.COLORS['empty_soil_color'])
        sleep(1)
        worked_on_field = self.find_first_pixel(target_color=self.COLORS['worked_on_soil_color'])
        if worked_on_field and empty_field:
            print("There is a currently worked on soil")
            worked_on_x, worked_on_y = worked_on_field
            empty_x, empty_y = empty_field
            if empty_x <= worked_on_x and empty_y <= worked_on_y:
                return 'empty'
            else:
                return 'worked_on'
        elif worked_on_field and not empty_field:
            return 'worked_on'
        else:
            return 'plant'

    def create_scaled_locations(self):
        self.errors_notifier = 9
        print("trying to get the canvas size")
        try:
            canvas = self.driver.find_element(By.TAG_NAME, 'canvas')
        except NoSuchElementException:
            print("Inside the Exception try block for getting the canvas element - for some reason crushed")
            return None
        else:
            print("Got the canvas element successfully ")
            canvas_size = canvas.size
            canvas_text = canvas.text
            print(canvas_text)
            print(type(canvas_text))
            print(canvas_size)
            print(type(canvas_size))
            canvas_width = canvas_size["width"]
            canvas_height = canvas_size["height"]
            print("was able to transform into a dic")
            rational_locations = {'travel_img_location': (0.14081632653061224, 0.19351464435146443),
                                  'go_to_terravilla_button_location': (0.4802721088435374, 0.33682008368200833),
                                  'infiniportal_location': (0.710204081632653, 0.5512552301255229),
                                  'infiniportal_input_box': (0.5299319727891156, 0.4623430962343096),
                                  'store_search_box': (0.4020408163265306, 0.41841004184100417),
                                  'store_sell_tab_location': (0.7047619047619047, 0.3598326359832636),
                                  'buysell_max_button_location': (0.6210884353741496, 0.6903765690376569),
                                  'input_quantity_location': (0.5285714285714286, 0.7018828451882845),
                                  'confirm_buysell_location': (0.5061224489795918, 0.811715481171548),
                                  'log_out_button_location': (0.9775510204081632, 0.37656903765690375),
                                  'profile_clicked_by_mistake': (0.38095238095238093, 0.27928870292887026),
                                  'large_map_button': (0.02040816326530612, 0.37656903765690375),
                                  }
            scaled_locations = {key: (value[0] * canvas_width, value[1] * canvas_height) for key, value in
                                rational_locations.items()}
            print(f"corrected locations: {scaled_locations}")
            return scaled_locations

    def look_for_profile_mistake(self):
        self.errors_notifier = 10
        try:
            exit_profile_button = self.driver.find_element(By.CLASS_NAME, 'Profile_closeButton__1n0Um')
        except NoSuchElementException:
            pass
        else:
            exit_profile_button.click()
            sleep(1)

    def look_for_bookmark_tab_mistake(self):
        self.errors_notifier = 11
        try:
            exit_profile_button = self.driver.find_element(By.CLASS_NAME, 'commons_closeBtn__UobaL')
        except NoSuchElementException:
            pass
        else:
            exit_profile_button.click()
            sleep(1)

    def look_for_quests_tab_mistake(self):
        self.errors_notifier = 12
        try:
            exit_profile_button = self.driver.find_element(By.CLASS_NAME, 'commons_pushbutton__7Tpa3')
        except NoSuchElementException:
            pass
        else:
            exit_profile_button.click()
            sleep(1)

    def get_energy_amount(self):
        self.errors_notifier = 13
        got_energy = False
        counter = 0
        while not got_energy:
            try:
                energy_amount_str = str(self.driver.find_element(By.CLASS_NAME, 'Hud_energytext__3PQZQ').text)
            except NoSuchElementException:
                continue
            else:
                energy_amount_str = energy_amount_str.replace(",", "")
                energy_amount_float = float(energy_amount_str)
                return energy_amount_float
            finally:
                counter += 1
                if counter >= 20:
                    break

    def skip_dialog(self):
        self.errors_notifier = 14
        sleep(3)
        skip_button_class = 'GameDialog_skip__Y5RGE'
        while True:
            try:
                skip_button = self.driver.find_element(By.CLASS_NAME, skip_button_class)
            except NoSuchElementException:
                print('Dialog probably over')
                break
            else:
                skip_button.click()
                print('skip button clicked ')
                continue
            finally:
                sleep(0.5)

    def get_berry_amount(self):
        self.errors_notifier = 15
        wallet = self.driver.find_element(By.CLASS_NAME, 'commons_coinBalance__d9sah').text
        if ',' in wallet:
            wallet = float(wallet.replace(',', ''))
        else:
            wallet = float(wallet)
        if wallet:
            return wallet

    def center_pointer(self):
        self.errors_notifier = 16
        full_x, full_y = pyautogui.size()
        center_x = full_x / 2
        center_y = full_y / 2
        pyautogui.moveTo(center_x, center_y)

    def click_on_directions(self, clicking_dic: dict):
        self.errors_notifier = 17
        for key, value in clicking_dic.items():
            if value is not None:
                self.center_pointer()
                current_x, current_y = pyautogui.position()
                if key == 'up':  # click up
                    pyautogui.moveTo(current_x, current_y + value)
                    pyautogui.click()
                if key == 'down':
                    pyautogui.moveTo(current_x, current_y - value)
                    pyautogui.click()
                if key == 'right':
                    pyautogui.moveTo(current_x + value, current_y)
                    pyautogui.click()
                if key == 'left':
                    pyautogui.moveTo(current_x - value, current_y)
                    pyautogui.click()
                if 'costume' in key:
                    new_x = current_x + value[0]
                    new_y = current_y + value[1]
                    pyautogui.moveTo(new_x, new_y)
                    pyautogui.click()
                self.look_for_profile_mistake()
                self.look_for_bookmark_tab_mistake()
                self.look_for_quests_tab_mistake()

    def get_code_from_mail_7(self, mail7_mail):
        self.errors_notifier = 18
        code = False
        counter = 0
        self.driver.execute_script("window.open('', '_blank');")
        sleep(3)
        self.driver.switch_to.window(self.driver.window_handles[1]), sleep(1)
        self.driver.get('https://www.mail7.io/'), sleep(2)
        input_mail7_mail = self.driver.find_element(By.XPATH,
                                                    '/html/body/main/section[2]/div/form/div[1]/input[1]')
        input_mail7_mail.send_keys(mail7_mail)
        sleep(2)
        self.driver.find_element(By.XPATH, '/html/body/main/section[2]/div/form/div[1]/input[2]').click()
        while not code:
            try:
                sleep(8)
                email_with_the_code = self.driver.find_elements(By.CLASS_NAME, 'mail-col')[2]
                email_with_the_code.click()
            except Exception as getting_code_from_mail_7:
                print("Mail 7 exception triggered")
                self.driver.get('https://www.mail7.io/'), sleep(2)
                input_mail7_mail = self.driver.find_element(By.XPATH,
                                                            '/html/body/main/section[2]/div/form/div[1]/input[1]')
                input_mail7_mail.send_keys(mail7_mail)
                sleep(2)
                self.driver.find_element(By.XPATH,
                                         '/html/body/main/section[2]/div/form/div[1]/input[2]').click(), sleep(2)
                if counter >= 4:
                    print("Should crush now")
                    raise Exception(f"Error trying to get the code from mail 7 {getting_code_from_mail_7}")
            else:
                sleep(6)
                text = self.driver.find_element(By.TAG_NAME, "body").text
                code_end_location = str(text).find('is your one-time code')
                end = int(code_end_location) - 1
                start = end - 7
                code = str(text)[start:end].strip(' ')
                return code
            finally:
                counter += 1

    def start_game_with_existing_account(self):
        self.errors_notifier = 19
        self.driver.maximize_window()
        self.driver.get(self.website)
        sleep(5)
        log_in = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[3]/div[2]/div[1]/button[1]')
        log_in.click(), sleep(3)
        email_radio_xpath = '//*[@id="__next"]/div/div[3]/div[2]/div[1]/div[2]/div[1]/label[3]/input'
        email_radio = self.driver.find_element(By.XPATH, email_radio_xpath)
        email_radio.click(), sleep(4)
        email_input = self.driver.find_element(By.XPATH,
                                               '/html/body/div[1]/div/div[3]/div[2]/div[1]/div[2]/div[2]/input')
        email_input.send_keys(f'{self.email}'), sleep(2)
        pyautogui.press('enter')
        sleep(1)
        mail_7_code = self.get_code_from_mail_7(mail7_mail=self.email)
        sleep(1)
        pyautogui.hotkey(self.ctrl_keyboard, "w")
        self.driver.switch_to.window(self.driver.window_handles[0]), sleep(1)
        sleep(2)
        pyautogui.typewrite(f'{mail_7_code}')
        sleep(3)
        pyautogui.hotkey('enter')
        sleep(4)
        start_game_button = self.driver.find_element(By.XPATH,
                                                     '//*[@id="__next"]/div/div[3]/div[2]/button[1]')
        start_game_button.click()
        sleep(6)

    def add_to_bookmarks(self):
        self.errors_notifier = 20
        print("Trying to add to bookmark")
        for color in self.COLORS['land_sign_color']:
            looking_for_sign = self.find_first_pixel(color)
            print(bool(looking_for_sign))
            print(looking_for_sign)
            if looking_for_sign:
                "Entered the if statement, sign pixel was found"
                x, y = looking_for_sign
                new_x = x + 40
                pyautogui.doubleClick(new_x, y)
                sleep(3)
                try_button_bookmark = self.driver.find_elements(By.CLASS_NAME, 'commons_uikit__Nmsxg')  #
                if try_button_bookmark:
                    sleep(2)
                    try_button_bookmark[1].click()
                    sleep(1)
                    pyautogui.hotkey("esc")
                    return True
            else:
                print(f"land color was not found for this {color}")
                sleep(2)
                pyautogui.hotkey("esc")
        sleep(1)
        pyautogui.hotkey("esc")
        self.send_image_email(body_text="Didn't succeed in locating bookmark color",
                              target_mail=self.mail_for_errors[0])
        return False

    def reset_to_terravilla(self):
        self.errors_notifier = 21
        print("Trying to reset terravilla")
        sleep(2)
        pyautogui.hotkey("esc")
        self.make_sure_game_is_on()
        pyautogui.doubleClick(self.LOCATIONS['travel_img_location'])
        sleep(1.5)
        self.driver.find_elements(By.CLASS_NAME, "LandAndTravel_tab__LD39V")[2].click()  # bookmarks_button
        sleep(1.5)
        all_my_bookmarks = self.driver.find_elements(By.CLASS_NAME, "LandAndTravel_mapSquare__LuVEh")
        if bool(all_my_bookmarks):
            first_bookmark = all_my_bookmarks[0]
            first_bookmark.find_element(By.TAG_NAME, "button").click()  # go_to_first_bookmark_button
            sleep(3)
            self.make_sure_game_is_on()
            pyautogui.doubleClick(self.LOCATIONS['travel_img_location'])
            sleep(3)
            pyautogui.doubleClick(self.LOCATIONS['go_to_terravilla_button_location'])
            sleep(4)
        else:
            raise Exception("User has no bookmarks and not centered")

    def get_to_color(self, target_color: tuple):
        self.errors_notifier = 22
        if self.find_first_pixel(target_color=target_color):
            pressing_counter = 0
            overall_presses = 0
            got_to_color = False
            while not got_to_color:
                old_press_x, old_press_y = pyautogui.position()
                self.press_on_color(target_color=target_color)
                new_press_x, new_press_y = pyautogui.position()
                overall_presses += 1
                # if overall_presses >= 150:
                #     return False
                if old_press_x == new_press_x and old_press_y == new_press_y:
                    print(f"Focused on point {new_press_x, new_press_y}")
                    pressing_counter += 1
                    if pressing_counter >= 3 or overall_presses % 15 == 0:
                        if (self.range_middle_x[0] < new_press_x < self.range_middle_x[1]
                                and self.range_middle_y[0] < new_press_y < self.range_middle_y[1]):
                            print("Got to the wanted color")
                            return True
                        else:
                            print("Probably stuck")
                            directions = ['left', 'up']
                            for d in directions:
                                keyboard_move_figure(direction=d, duration=0.55)
                                pressing_counter = 0
                                overall_presses = 0

        else:
            print("Color is not even on the screen")
            return False

    def center_terravilla(self):
        self.errors_notifier = 23
        print("Trying to Get to fountain terravilla")
        sleep(3)
        pyautogui.hotkey("esc")
        pyautogui.doubleClick(self.LOCATIONS['travel_img_location'])
        sleep(2)
        pyautogui.doubleClick(self.LOCATIONS['go_to_terravilla_button_location'])
        sleep(2)
        self.make_sure_game_is_on()
        sleep(2)
        fountain_in_sight = False
        while not fountain_in_sight:
            if bool(self.find_first_pixel(target_color=self.COLORS["center_color"])):
                fountain_in_sight = True
            else:
                self.reset_to_terravilla()
        self.get_to_color(target_color=self.COLORS["center_color"])

    def make_sure_in_shop(self):
        self.errors_notifier = 24
        in_shop = False
        counter = 0
        while not in_shop:
            sleep(2)
            image = ImageGrab.grab().convert(mode="RGB").resize(self.expected_size)
            if image.getpixel((170, 630)) == self.COLORS["black_in_shop"]:
                return True
            else:
                print("Not in shop")
                counter += 1
                if counter >= 6:
                    return False

    def go_to_farm(self, farm_number=2498, add_to_bookmarks: bool = True):
        self.errors_notifier = 25
        print(f"Trying to go to the farm {farm_number}")
        pyautogui.doubleClick(self.LOCATIONS['travel_img_location'])
        sleep(2)
        pyautogui.doubleClick(self.LOCATIONS['go_to_terravilla_button_location'])
        sleep(2)
        self.make_sure_game_is_on()
        sleep(2)
        in_farm = False
        pyautogui.doubleClick(self.LOCATIONS['travel_img_location'])
        sleep(1.5)
        self.driver.find_elements(By.CLASS_NAME, "LandAndTravel_tab__LD39V")[2].click()  # bookmarks_button
        sleep(1.5)
        all_my_bookmarks = self.driver.find_elements(By.CLASS_NAME, "LandAndTravel_mapSquare__LuVEh")
        if bool(all_my_bookmarks):
            for bookmark in all_my_bookmarks:
                if str(farm_number) in bookmark.text:
                    bookmark.find_element(By.TAG_NAME, "button").click()
                    self.make_sure_game_is_on()
                    in_farm = True
                    add_to_bookmarks = False
        print(f"{farm_number} not in Bookmarks, trying to go with the infiniportal")
        pyautogui.hotkey("esc")
        sleep(1)
        pyautogui.hotkey("esc")
        sleep(1)
        in_ranger_shop = False
        while not in_ranger_shop and not in_farm:
            self.center_terravilla()
            sleep(5)
            pyautogui.keyDown('left')
            sleep(5.7)
            pyautogui.keyUp('left')
            self.make_sure_game_is_on()
            pyautogui.keyDown('up')
            sleep(6)
            pyautogui.keyUp('up')
            sleep(3)
            self.make_sure_game_is_on()
            if self.make_sure_in_shop():
                in_ranger_shop = True
            else:
                for improve in range(8):
                    self.press_on_color(target_color=self.COLORS['ranger_farms_shop_color'])
            sleep(2)
            pyautogui.keyDown('right')
            sleep(1.6)
            pyautogui.keyUp('right')
            pyautogui.keyDown('up')
            sleep(4)
            pyautogui.keyUp('up')
            sleep(2)
            pyautogui.doubleClick(self.LOCATIONS['infiniportal_location'], duration=0.3)
            sleep(1)
            pyautogui.click(x=self.LOCATIONS['infiniportal_location'][0],
                            y=self.LOCATIONS['infiniportal_location'][1],
                            duration=0.3)
            sleep(2.5)
            try:
                farm_search = self.driver.find_element(By.TAG_NAME, 'input')
            except NoSuchElementException as ranger_error:
                self.record_error(f'ranger error {ranger_error} username: {self.username}')
                self.center_terravilla()
                self.go_to_farm(farm_number=farm_number, add_to_bookmarks=add_to_bookmarks)
            else:
                counter = 0
                while f'{farm_number}' not in str(farm_search.get_attribute('value')):
                    print(str(farm_search.get_attribute('value')))
                    farm_search.clear()
                    sleep(1)
                    farm_search.send_keys(f'{farm_number}')
                    sleep(2)
                    farm_search = self.driver.find_element(By.TAG_NAME, 'input')
                    counter += 1
                    if counter >= 3:
                        break
                pyautogui.hotkey('enter')
                sleep(4)
                in_farm = True
            self.make_sure_game_is_on()
            sleep(2)
            if in_farm and add_to_bookmarks:
                self.add_to_bookmarks()

    def arrange_inventory_details(self, item_slicer=18):
        """
        A function that goes through each square in the inventory and returns its whereabouts. For example: 1: 'shears'
        :return: dict
        """
        self.errors_notifier = 26
        self.center_pointer()
        # global item, seeds
        seeds = None
        sleep(2)
        pyautogui.hotkey("b")
        sleep(2)
        location_in_inventory = 0
        arranged_inventory = {}
        the_name_of_square_inventory_div_class = 'Hud_item__YGtIC'
        the_name_of_square_inventory_div_class_with_an_item_in_it = "clickable"
        all_items_in_the_inventory = self.driver.find_elements(By.CLASS_NAME,
                                                               the_name_of_square_inventory_div_class)
        self.driver.save_screenshot("screenshot.png")
        sleep(2)
        screenshot = Image.open("screenshot.png")
        selenium_screenshot_width = screenshot.width
        selenium_screenshot_height = screenshot.height
        image = ImageGrab.grab().convert(mode="RGB").resize(self.expected_size)
        image.save("screenshot.png")
        sleep(2)
        print(f"Items in all squares inventory: should be 18: {all_items_in_the_inventory}")
        screenshot = Image.open("screenshot.png")
        x_sel_real_ratio = selenium_screenshot_width / screenshot.width
        y_sel_real_ratio = selenium_screenshot_height / screenshot.height
        for square in all_items_in_the_inventory[:item_slicer]:
            sleep(0.5)
            location_in_inventory += 1
            item = None
            try:
                item_in_square = square.find_element(By.CLASS_NAME,
                                                     the_name_of_square_inventory_div_class_with_an_item_in_it)
            except Exception as square_item_empty_error:
                print(f"Square item empty {str(square_item_empty_error)[:15]}")
            else:
                item = 'Unknown'
                # Get the location and size of the element
                location = item_in_square.location
                print(f"Item location is {location}")
                size = item_in_square.size
                print(f"Item location is {size}")
                print(f"Expected size is {self.expected_size}")
                print(f"Selenium screenshot size is {screenshot.size}")
                absolute_left_x, absolute_left_y = self.LOCATIONS["inventory_first_location"]
                multiplier_x = 0
                multiplier_y = 0
                if location_in_inventory <= 6:
                    multiplier_y = 0
                    multiplier_x = location_in_inventory - 1
                elif 6 < location_in_inventory <= 12:
                    multiplier_x = location_in_inventory - 7
                    multiplier_y = 1
                elif 12 < location_in_inventory <= 18:
                    multiplier_x = location_in_inventory - 13
                    multiplier_y = 2
                location['x'] = multiplier_x * self.inventory_gap_x + absolute_left_x
                location['y'] = multiplier_y * self.inventory_gap_y + absolute_left_y
                left = location['x']
                top = location['y']
                right = location['x'] + size['width'] * x_sel_real_ratio + 15
                bottom = location['y'] + size['height'] * y_sel_real_ratio + 20
                print(
                    f"inventory location: {location_in_inventory}. absolute x, y {absolute_left_x}, {absolute_left_y}."
                    f"multiplier x, y {multiplier_x}, {multiplier_y}. location x {left} top y {top}")
                element_screenshot = screenshot.crop((left, top, right, bottom))
                # Save the screenshot of the element
                element_screenshot.save("element_screenshot.png")
                for seeds_package_color in self.COLORS["Seeds_package"]:
                    if bool(self.find_first_pixel(target_color=seeds_package_color, image=element_screenshot,
                                                  from_arrange=True)):
                        seeds = True
                        break
                    else:
                        seeds = False
                for key, value in self.COLORS["dominant_colors"].items():
                    for color in value:
                        if bool(self.find_first_pixel(target_color=color, image=element_screenshot, from_arrange=True)):
                            print(f"Found the color {color} for {key}")
                            if seeds:
                                item = f"{key} Seeds"
                            else:
                                item = f"{key}"
                            with_value_square = all_items_in_the_inventory[location_in_inventory - 1]
                            square_quantity = with_value_square.find_element(By.CLASS_NAME, 'Hud_quantity__V_YWQ')
                            print(f"This is square quantity.text {square_quantity.text}")
                            if 'x' in square_quantity.text:
                                print(f'Current quantity, {square_quantity.text}')
                                number_of_quantity = square_quantity.text[1:]
                                number_of_quantity = int(number_of_quantity.replace(',', ''))
                            else:
                                number_of_quantity = 1
                            details = item, number_of_quantity
                            item = details
                            break
            finally:
                arranged_inventory[location_in_inventory] = item
        print(f"Final arranged inventory is {arranged_inventory}")
        pyautogui.hotkey("b")
        return arranged_inventory

    def query_inventory(self, query):
        self.errors_notifier = 27
        form = {
        }
        if isinstance(query, str):
            print("Query is a string inputted")
            print(f"Requested to find out about {query}")
            for key, value in self.arranged_inventory.items():
                if isinstance(value, tuple):
                    if value[0] == query:
                        print(f"Your item was found in location {key} in the inventory")
                        form["inventory_location"] = key
                        details = self.arranged_inventory[key]
                        form["item_name"] = details[0]
                        form["quantity"] = details[1]
                        print(form)
                        return form
                elif isinstance(query, int):
                    print("Query is an int inputted")
                    print(f"taking out the details in location {query}")
                    form["inventory_location"] = query
                    details = self.arranged_inventory[query]
                    if bool(details):
                        print(f"item requested at location {query} is {details}")
                        form["item_name"] = details[0]
                        form["quantity"] = details[1]
                        print(form)
                        return form
                    else:
                        print("There is no such number in the inventory. please provide a number between 1-18.")
        return False

    def click_on_all_the_field(self, soil_color: tuple, item_name: str, inventory_location: int, rows=6, columns=10,
                               distance_field=0.26, **kwargs):
        self.errors_notifier = 28
        print("Trying to click on all the field")
        columns = columns / 2
        if columns % 2 != 0:
            columns = columns + 0.5
        columns = int(columns)
        sleep(1)
        for get_close in range(self.get_close_to_the_soil):
            self.press_on_color(soil_color)
        if kwargs:
            print("Additional Correction:")
            for key, value in kwargs.items():
                keyboard_move_figure(key, value)
        tabs_needed_before = 0
        tabs_needed_after = 0
        if 1 <= int(inventory_location) <= 6:
            tabs_needed_before = 0
            tabs_needed_after = 0
        elif 6 <= int(inventory_location) <= 12:
            tabs_needed_before = 1
            tabs_needed_after = 2
        elif 13 <= int(inventory_location) <= 18:
            tabs_needed_before = 2
            tabs_needed_after = 1
        inventory_location = inventory_location - (6 * tabs_needed_before)
        for tabs in range(tabs_needed_before):
            pyautogui.hotkey("tab")
            sleep(0.2)
        pyautogui.hotkey(str(inventory_location))
        for field in range(columns):
            self.click_on_directions(self.clicking_fields_dict)
            if field == columns - 1:
                continue
            keyboard_move_figure('right', duration=distance_field * 2)
            sleep(1)
        pyautogui.hotkey(str(inventory_location))
        for tabs in range(tabs_needed_after):
            pyautogui.hotkey("tab")
            sleep(0.2)

    def go_to_hazels_counter(self):
        self.errors_notifier = 29
        print("Trying to go to bucks store ")
        in_bucks_shop = False
        while not in_bucks_shop:
            self.center_terravilla()
            keyboard_move_figure('right', 5.12)
            keyboard_move_figure('up', 1)
            sleep(2)
            self.make_sure_game_is_on()
            if self.make_sure_in_shop():
                in_bucks_shop = True

        sleep(2)
        self.make_sure_game_is_on()
        keyboard_move_figure('right', 3.3)
        keyboard_move_figure('up', 2)

    def sell_goods(self, items_to_sell_dict: dict):
        self.errors_notifier = 30
        print(f"Trying to sell the goods {items_to_sell_dict}")
        sleep(2)
        self.make_sure_game_is_on()
        if self.make_sure_in_shop():
            pass
        else:
            self.center_terravilla()
            self.go_to_hazels_counter()
        if items_to_sell_dict:
            for key, value in items_to_sell_dict.items():
                pyautogui.hotkey('esc')
                item_to_sell = key
                quantity_to_sell = value
                x_desk, y_desk = self.press_on_color(target_color=self.COLORS["sell_desk_color"])
                x_desk -= 20
                y_desk -= 20
                pyautogui.doubleClick(x=x_desk, y=y_desk)
                sleep(2)
                store_sell_class = 'Store_sellButton__F9vtc'
                try:
                    self.driver.find_element(By.CLASS_NAME, store_sell_class).click()
                except NoSuchElementException as sell_error:
                    self.record_error(f'Store sell error {sell_error} username: {self.username}')
                    return False
                else:
                    sleep(2)
                    all_items_for_sale_class = 'Store_card-title__InPpB'
                    all_items_for_sale = self.driver.find_elements(By.CLASS_NAME,
                                                                   f'{all_items_for_sale_class}')
                    for for_sell_item in all_items_for_sale:
                        if f'{item_to_sell}' in for_sell_item.text and 'Seeds' not in for_sell_item.text:
                            print("Should sell now!!")
                            for_sell_item.click()
                            sleep(1)
                    # Sell Max button
                    sleep(2)
                    if quantity_to_sell == 'max':
                        pyautogui.doubleClick(self.LOCATIONS['sell_max_button_location'])
                    else:
                        self.center_pointer()
                        pyautogui.click()
                        pyautogui.hotkey("tab")
                        sleep(0.2)
                        pyautogui.hotkey("tab")
                        sleep(1)
                        pyautogui.typewrite(f'{quantity_to_sell}')
                    sleep(2)
                    # confirm sell
                    sleep(1.5)
                    pyautogui.doubleClick(self.LOCATIONS['confirm_sell_location'])
                    sleep(1)
                finally:
                    pyautogui.hotkey('esc')
        else:
            print("No Items were inputted for sale")

    def buy_goods(self, items_to_buy_dict: dict):
        sleep(2)
        self.errors_notifier = 31
        self.make_sure_game_is_on()
        if self.make_sure_in_shop():
            pass
        else:
            self.center_terravilla()
            self.go_to_hazels_counter()
        print(f"Trying to buy items {items_to_buy_dict}")
        print(type(items_to_buy_dict))
        if items_to_buy_dict:
            for key, value in items_to_buy_dict.items():
                item_to_buy = key
                quantity_to_buy = value
                pyautogui.hotkey('esc')
                sleep(2)
                x_desk, y_desk = self.press_on_color(target_color=self.COLORS["sell_desk_color"])
                x_desk += 20
                y_desk += 30
                pyautogui.doubleClick(x=x_desk, y=y_desk)
                sleep(5)
                try:
                    self.driver.find_element(By.CLASS_NAME, 'Store_filter__qtqd7').send_keys(item_to_buy)
                except NoSuchElementException as store_buy_error:
                    self.record_error(f'Store Buy Error {store_buy_error} username: {self.username}')
                    pyautogui.hotkey('esc')
                    return False
                else:
                    cards_founded_titles = 'Store_card-title__InPpB'
                    sleep(3)
                    self.driver.find_element(By.CLASS_NAME, cards_founded_titles).click()
                    sleep(3)
                    if quantity_to_buy == 'max':
                        pyautogui.click(self.LOCATIONS["buy_max_button_location"])
                    else:
                        self.center_pointer()
                        pyautogui.click()
                        pyautogui.hotkey("tab")
                        sleep(0.2)
                        pyautogui.hotkey("tab")
                        sleep(1)
                        pyautogui.typewrite(f'{quantity_to_buy}')
                    sleep(2.5)
                    # confirm Buy
                    pyautogui.doubleClick(self.LOCATIONS['confirm_buy_location'])
                    sleep(1.5)
            pyautogui.hotkey('esc')
            sleep(1)
            pyautogui.hotkey('esc')
        else:
            print("There were no items to buy given")

    def discover_farming_level(self):
        self.errors_notifier = 32
        sleep(2)
        pyautogui.click(self.LOCATIONS["star_icon_location"])
        try:
            farming_level = int(self.driver.find_element(By.CLASS_NAME, "Skills_skillPoints__xvU6j").text)
            sleep(1.5)
            self.driver.find_element(By.CLASS_NAME, 'commons_closeBtn__UobaL').click()
        except NoSuchElementException as farming_level_exception:
            self.record_error(f"error at trying to get the farming level {farming_level_exception}")
            return False
        else:
            return farming_level
