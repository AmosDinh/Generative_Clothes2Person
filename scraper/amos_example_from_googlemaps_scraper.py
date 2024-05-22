# https://github.com/AmosDinh/CNNBirdseye/blob/main/maps_builder.py


from playwright.sync_api import sync_playwright
import uuid
import os
def remove_all_background(page):
    remove = ["#omnibox-singlebox",".scene-footer-container", '.app-bottom-content-anchor','#play','.scene-footer-container', '#watermark','#titlecard', '#image-header']
    for selector in remove:
        page.evaluate(f"""selector => document.querySelector(selector).style.opactiy = 0 """, selector)
        
    
    
    
    
    # all buttons: display none
    # buttons = page.query_selector_all('button')
    # for button in buttons:
    #     parent = button.query_selector('xpath=..')
    #     # check if parent only has buttons as children
    #     children = parent.query_selector_all('div')
    #     if len(children) == 0:
    #         page.evaluate(f"""element => element.style.display = "none" """, parent)
    #     # page.evaluate(f"""element => element.style.display = "none" """, parent)
        
def get_pegman_background_position_y(page):
    minimap_div = page.query_selector('#minimap')
    pegman_div = minimap_div.query_selector("div[style*='rotating-1x.png']")
    background_position_y = page.evaluate('(element) => getComputedStyle(element).backgroundPositionY', pegman_div)
    # -364px to int
    y = int(background_position_y.replace("px", ""))

    return y

def get_parent_parent_pegman_translate(page):
    minimap_div = page.query_selector('#minimap')
    pegman_div = minimap_div.query_selector("div[style*='rotating-1x.png']")
    grandparent = pegman_div.query_selector('xpath=../..')
    #grandparent = parent.evaluate("""parent => parent.parentElement""")
    # get the translate x, and y
    translate = page.evaluate('(element) => getComputedStyle(element).transform', grandparent)
    x, y = translate.replace("matrix(", "").replace(")", "").split(", ")[-2:]
    x = int(x)
    y = int(y)
    return x, y

def mouse_drag_on_minimap(page, x_amount, y_amount):
    # get center of minimap
    #minimap_div = page.query_selector('#minimap')
    minimap_div = page.query_selector('[aria-label="Interaktive Karte"]').query_selector('xpath=..')
    center_x = minimap_div.bounding_box()["x"] + minimap_div.bounding_box()["width"] / 2
    center_y = minimap_div.bounding_box()["y"] + minimap_div.bounding_box()["height"] / 2
    print(center_x, center_y)
    print(minimap_div.bounding_box())
    # focus on minimap
    # minimap_div.click()
    print('click')
    while minimap_div.bounding_box()["width"]!=222 or minimap_div.bounding_box()["height"]!=222:
        #page.mouse.move(center_x, center_y)
        minimap_div.hover()
        minimap_div = page.query_selector('[aria-label="Interaktive Karte"]').query_selector('xpath=..')
        
    minimap_div = page.query_selector('[aria-label="Interaktive Karte"]').query_selector('xpath=..')
    center_x = minimap_div.bounding_box()["x"] + minimap_div.bounding_box()["width"] / 2
    center_y = minimap_div.bounding_box()["y"] + minimap_div.bounding_box()["height"] / 2
    page.mouse.move(center_x, center_y)
    page.mouse.down()
    page.mouse.move(center_x+x_amount, center_y+y_amount)
    page.mouse.up()
    minimap = page.query_selector('#minimap')
    first_child = minimap.query_selector_all('xpath=child::*')[0]
    second_child = first_child.query_selector_all('xpath=child::*')[1]
    third_child = second_child.query_selector_all('xpath=child::*')[2]
    fourth_child = second_child.query_selector_all('xpath=child::*')[3]
    # displaynone
    page.evaluate(f"""element => element.style.display = "none" """, third_child)
    page.evaluate(f"""element => element.style.display = "none" """, fourth_child)

def move_map_to_center(page):
    center_x = 110
    center_y = 110
    #map_ = page.locator('[aria-label="Interaktive Karte"]')
    margin = 2
    while True:
        x, y = get_parent_parent_pegman_translate(page)
        if abs(center_x-x)<margin and abs(center_y-y)<margin:
            break
        # drag mouse
        if x < center_x or y < center_y or x > center_x or y > center_y:
            mouse_drag_on_minimap(page, center_x-x, center_y-y)
        

    

def rotate_to(page, angle):
    # define top as 0°
    # define right as 90°
    # define bottom as 180°
    # define left as 270°
    # -780 is the maximum value for the background-position-y (top)
    # -780 = 2pi = 0
    #degree_of_freedom = 32
    # = degree_of_freedom/2
    # 0 is the minimum
    
    # angle to nearest 24 degrees
    angle = round(angle / 24) * 24
    
    page.locator('[aria-label="Street View"]').click()
    page.keyboard.down("ArrowRight")
    while True:
        
        y = get_pegman_background_position_y(page)
        
        current_angle = abs(y / -780 * 360)
        
        if abs(angle-current_angle) < 1 or abs(angle-current_angle) > 359:
            page.keyboard.up("ArrowRight")
            break
    page.keyboard.up("ArrowRight")
    print('done', angle)

import cv2
import numpy as np 
def click_on_interactive_street(page):  
    
    page.click('[aria-label="Street View-Abdeckung anzeigen"]')
    page.wait_for_timeout(2000)
    # analyze the image, get all the walkable sections by color
    # read in the image as a numpy array
    blue_pixels = [0]
    name = f"cache/google_maps_temp.png"
    #while os.path.exists(name):
    #    name = f"cache/google_maps_temp{str(uuid.uuid4())}.png"
        
    for _ in range(5):
        
        page.screenshot(path=name)
        img = cv2.imread(name)
        # delete img
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        blue_color = [3, 169, 244]
        blue_color2 = [18,158,175]
        # get all the blue pixels
        blue_pixels1 = (img[:,:,0] == blue_color[0]) & (img[:,:,1] == blue_color[1]) & (img[:,:,2] == blue_color[2])
        blue_pixels2 = (img[:,:,0] == blue_color2[0]) & (img[:,:,1] == blue_color2[1]) & (img[:,:,2] == blue_color2[2])
        
        if np.sum(blue_pixels1) > np.sum(blue_pixels2):
            blue_pixels = blue_pixels1
            break
        elif np.sum(blue_pixels1) < np.sum(blue_pixels2):
            blue_pixels = blue_pixels2
            break
        
        page.wait_for_timeout(2000)
        
    if np.sum(blue_pixels) == 0:
        print('no blue pixels')
        
        
        return False
    else:
        # mask back to full image with 
        # click on random blue pixel in the upper half, center of the image
        left =  img.shape[1]//4
        right = img.shape[1]-img.shape[1]//4
        top = img.shape[0]//4
        bottom = img.shape[0]-img.shape[0]//4
        
        upper_center_img_mask = np.zeros_like(img[:,:,0])
        upper_center_img_mask[:top, left:right] = 1
        upper_center_img_mask = np.array(np.where((upper_center_img_mask==1) & (blue_pixels==1)))
        
        lower_center_img_mask = np.zeros_like(img[:,:,0])
        lower_center_img_mask[bottom:, left:right] = 1
        lower_center_img_mask = np.array(np.where((lower_center_img_mask==1) & (blue_pixels==1)))
        
        left_img_mask = np.zeros_like(img[:,:,0])
        left_img_mask[:, :left] = 1
        left_img_mask = np.array(np.where((left_img_mask==1) & (blue_pixels==1)))
        
        right_img_mask = np.zeros_like(img[:,:,0])
        right_img_mask[:, right:] = 1
        right_img_mask = np.array(np.where((right_img_mask==1) & (blue_pixels==1)))
                
        all_img_mask = np.array(np.where(blue_pixels==1))

        # while '[jsaction="compass.needle"]' not visible/ not on page
        while page.query_selector('[jsaction="compass.needle"]') == None:
            # if at least one in lower_center_img_mask
            if len(right_img_mask[0]) > 0:
                random_indices_with_1 = np.random.choice(np.arange(len(right_img_mask[0])))
                random_indices_with_1 = right_img_mask[:, random_indices_with_1]
            elif len(upper_center_img_mask[0]) > 0:
                # click on random pixel in lower_center_img_mask which has a blue pixel
                random_indices_with_1 = np.random.choice(np.arange(len(upper_center_img_mask[0])))
                random_indices_with_1 = upper_center_img_mask[:, random_indices_with_1]
                
            elif len(lower_center_img_mask[0]) > 0:
                random_indices_with_1 = np.random.choice(np.arange(len(lower_center_img_mask[0])))
                random_indices_with_1 = lower_center_img_mask[:, random_indices_with_1]
                
            elif len(left_img_mask[0]) > 0:
                random_indices_with_1 = np.random.choice(np.arange(len(left_img_mask[0])))  
                random_indices_with_1 = left_img_mask[:, random_indices_with_1]
                
           
            else:
                random_indices_with_1 = np.random.choice(np.arange(len(all_img_mask[0])))
                random_indices_with_1 = all_img_mask[:, random_indices_with_1]

            # click on coordinate
            x = random_indices_with_1[1]
            y = random_indices_with_1[0]
            page.mouse.click(int(x), int(y))
            page.wait_for_timeout(1000)
            
    
def launch_google_maps(search_input):
    # change playwright timeout
    
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)#args=['--profile-directory=Default'])
        page = browser.new_page()
        page.set_default_timeout(6000)
        page.goto("https://www.google.com/maps")
        accept_button_selector = '[aria-label="Alle akzeptieren"]'
        page.click(accept_button_selector)
        
        search_input_name = '[name="q"]'
        page.type(search_input_name, search_input)
        accept_button_selector = '[aria-label="Suche"]'
        page.click(accept_button_selector)
        page.wait_for_timeout(2000)
        page.hover('[aria-labelledby="widget-minimap-icon-overlay"]')
        page.click('[jsaction="layerswitcher.quick.more"]')
        5
        page.click('[jsaction="layerswitcher.intent.spherical"]')
        page.click('[jsaction="layerswitcher.close"]')
        click_on_interactive_street(page)
        
        page.wait_for_timeout(3000)
        #page.hover('canvas')
        #page.click('#widget-zoom-out')
        # page.mouse.wheel(0, -1000)
        # page.wait_for_timeout(2000)
        
        # page.mouse.wheel(0, -1000)
        # page.wait_for_timeout(2000)
        
        # page.mouse.wheel(0, -1000)
        # page.mouse.wheel(0, 1000)
        # page.wait_for_timeout(2000)
        # page.mouse.wheel(0, 1000)
        # page.wait_for_timeout(2000)
        import uuid
        import datetime
        
        def click_foto(is_first_click):
            def screenshot(name):
                
                page.screenshot(path=name)
                
                
            name = 'images/'+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")+str(uuid.uuid4())+'_'+'_'.join(search_input.split(' '))
            #remove_all_background(page)
            page.click('[jsaction="compass.needle"]')  # face north
            expressions = [
                
                '.scene-footer',
                '#watermark',
                '.app-vertical-widget-holder',
                '#omnibox-container',
                '[jsaction="focus:titlecard.main"]',
                '#minimap',
                '[jsaction="imageheader.close"]',
                
            ]
            for expression in expressions:
                try:
                    page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, expression)
                except:
                    pass 
            try:
                page.evaluate(f"""selector => document.querySelector(selector).parentElement.style.opacity = 0 """, '[jsaction="imageheader.close"]')
            except:
                pass

            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '.scene-footer')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#watermark')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '.app-vertical-widget-holder')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#omnibox-container')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '[jsaction="focus:titlecard.main"]')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#minimap')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '[jsaction="imageheader.close"]')
            
            
            page.wait_for_timeout(500)
            screenshot(name+'_north.png')
            page.click('[jsaction="compass.right"]')
            page.wait_for_timeout(500)
            screenshot(name+'_east.png')
            
            page.click('[jsaction="compass.right"]')
            page.wait_for_timeout(500)
            screenshot(name+'_south.png')
            page.click('[jsaction="compass.right"]')
            page.wait_for_timeout(500)
            screenshot(name+'_west.png')
            page.click('[jsaction="compass.needle"]')
            page.wait_for_timeout(500)
            #page.hover('canvas')
            while page.query_selector('[aria-labelledby="widget-minimap-icon-overlay"]') == None:
                page.click('#widget-zoom-out')
                page.wait_for_timeout(1000)
                
            page.wait_for_timeout(2000)
            #page.click('#widget-zoom-out')
            if is_first_click:
                steuerfeld = page.query_selector('[jsaction="drawer.close;mouseover:drawer.showToggleTooltip; mouseout:drawer.hideToggleTooltip;focus:drawer.showToggleTooltip;blur:drawer.hideToggleTooltip"]')
                steuerfeld.click()
                is_first_click = False
            # opacity 0 using the steuerfeld handle
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '[aria-label="Seitliches Steuerfeld einblenden"]')
            # opacity button 0
            #page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '[jsaction="drawer.close;mouseover:drawer.showToggleTooltip; mouseout:drawer.hideToggleTooltip;focus:drawer.showToggleTooltip;blur:drawer.hideToggleTooltip"]')
            # #vasquette opacity 0
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#vasquette')
            # aria-label="Interaktive Karte" opacity 0
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#layer')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#minimap')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '.scene-footer')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '.widget-layer-shown')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#watermark')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '.app-vertical-widget-holder')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '[aria-label="Street View-Abdeckung anzeigen"]')
            # page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, '#runway-expand-button')
            
            expressions = [
                '[aria-label="Seitliches Steuerfeld einblenden"]',
                '#vasquette',
                '#layer',
                '#minimap',
                '.scene-footer',
                '.widget-layer-shown',
                '#watermark',
                '.app-vertical-widget-holder',
                '[aria-label="Street View-Abdeckung anzeigen"]',
                '#runway-expand-button',
                '[aria-roledescription="carousel"]'
            ]
            for expression in expressions:
                try:
                    page.evaluate(f"""selector => document.querySelector(selector).style.opacity = 0 """, expression)
                except:
                    pass
            try:
                page.evaluate(f"""selector => document.querySelector(selector).parentElement.parentElement.parentElement.parentElement.style.opacity = 0 """, '[jsaction="navigationrail.more"]')
            except:
                pass
            
           
            
            
            
            #page.click('#tilt')
            #page.wait_for_timeout(1000)
            #page.hover('[aria-labelledby="widget-minimap-icon-overlay"]')
            page.wait_for_timeout(2000)
            page.click('[aria-labelledby="widget-minimap-icon-overlay"]')
            page.wait_for_timeout(2000)
            page.click('[aria-label="Street View-Abdeckung anzeigen"]')
            page.click('[aria-label="Street View-Abdeckung anzeigen"]')
            page.wait_for_timeout(1500)
            screenshot(name+'_bev.png')
            page.click('[aria-label="Street View-Abdeckung anzeigen"]')
            page.wait_for_timeout(1000)
            page.click('#widget-zoom-out')
            page.wait_for_timeout(1000)
            page.click('#widget-zoom-out')
            #page.wait_for_timeout(1000)
            #page.click('#widget-zoom-out')
            page.wait_for_timeout(1000)
            click_on_interactive_street(page)
            
        is_first_click = True
        for _ in range(10):
            click_foto(is_first_click)
            is_first_click=False
        
        browser.close()
        
if __name__ == "__main__":
    import threading
    # launch_google_maps(search_input='Palo Alto CA')
    # while True:
    #     try: 
    #         launch_google_maps(search_input='Palo Alto CA')
    #     except:
    #        pass
        
    def worker(i):
        print(f'Starting worker {i}')
        launch_google_maps('Palo Alto CA')
        print(f'Finished worker {i}')

    num_workers = 1  # Change this to the number of workers you want
    # start thread but kill it after 5 min


    # threads = []
    # for i in range(num_workers):
    #     t = threading.Thread(target=worker, args=(i,))
    #     threads.append(t)
    #     t.start()

    # for t in threads:
    #     t.join()
    def run_worker_with_timeout(i, timeout):
        thread = threading.Thread(target=worker, args=(i,))
        thread.start()
        thread.join(timeout)  # Wait for the thread to finish or timeout
        if thread.is_alive():
            print(f"Worker {i} exceeded timeout, killing thread")
            thread._stop()  # This method is considered unsafe, use with caution

    num_workers = 1  # Change this to the number of workers you want
    timeout = 300  # 5 minutes in seconds

    while True:
        try:
            for i in range(num_workers):
                run_worker_with_timeout(i, timeout)
        except:
            pass