import pygame
import sys
import os
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pressure Cooker Simulation with Fuzzy Logic")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

current_dir = os.path.dirname(__file__)
background_image = pygame.image.load(os.path.join(current_dir, "images/kitchen.png"))
pressure_cooker_low = pygame.image.load(os.path.join(current_dir, "images/rmv4.png"))
pressure_cooker_medium = pygame.image.load(os.path.join(current_dir, "images/rmv.png"))
pressure_cooker_high = pygame.image.load(os.path.join(current_dir, "images/rmvv.png"))


pressure_level = 0
temperature = 0
weight = 0
thickness = 0
water_level = 0
font = pygame.font.Font(None, 36)
automatic_mode = False
last_time = pygame.time.get_ticks()
increase_temperature = False
shake_amplitude = 5
show_popup = False
remove_cooker = False

slider_x = 10
slider_y = 550
slider_width = 780
slider_height = 20
slider_handle_radius = 11

scales_x = 10
scales_y = 500

decrease_mode = False
decrease_timer = 0
decrease_interval = 10000
decrease_amount = 0.5

def temperature_membership(temp):
    low = max(0, (60 - temp) / 60)
    if temp < 70:
        medium = 0
    elif 70 <= temp <= 120:
        medium = (temp - 70) / 50
    else:
        medium = max(0, (190 - temp) / 70)

    high = max(0, (temp - 130) / 60)
    return low, medium, high

def weight_membership(weight):
    low = max(0, (50 - weight) / 30)
    medium = max(0, (weight - 50) / 20 if weight <= 70 else (70 - weight) / 30)
    high = max(0, (weight - 70) / 30)
    return low, medium, high

def thickness_membership(thickness):
    low = max(0, (5 - thickness) / 5)
    medium = max(0, (thickness - 3) / 2 if thickness <= 7 else (7 - thickness) / 3)
    high = max(0, (thickness - 7) / 3)
    return low, medium, high

def water_level_membership(water_level):
    low = max(0, (25 - water_level) / 35)
    medium = max(0, (water_level - 25) / 10 if water_level <= 35 else (35 - water_level) / 15)
    high = max(0, (water_level - 50) / 15)
    return low, medium, high

def fuzzy_inference(weight, thickness, water_level):
    low_weight, medium_weight, high_weight = weight_membership(weight)
    low_thickness, medium_thickness, high_thickness = thickness_membership(thickness)
    low_water, medium_water, high_water = water_level_membership(water_level)

    temperature_output = 0

    temperature_output += low_weight * low_thickness * low_water * 60
    temperature_output += medium_weight * medium_thickness * medium_water * 150
    temperature_output += high_weight * high_thickness * high_water * 220 
    temperature_output = min(max(int(temperature_output), 0), 300)

    return temperature_output

def calculate_pressure(temperature):
    if temperature < 60:
        return 0 
    elif 70 <= temperature <= 130:
        return (temperature - 70) / 60 * 100
    else:
        return min(100, (temperature - 130) / 70 * 200)


def draw_pressure_cooker(pressure_level):
    if remove_cooker:
        return

    shake_offset_x = 0
    shake_offset_y = 0

    if pressure_level > 133:
        shake_offset_x = shake_amplitude * random.uniform(-1, 1)
        shake_offset_y = shake_amplitude * random.uniform(-1, 1)

    if pressure_level <= 66:
        screen.blit(pressure_cooker_low, (300 + shake_offset_x, 200 + shake_offset_y))
    elif pressure_level <= 133:
        screen.blit(pressure_cooker_medium, (300 + shake_offset_x, 200 + shake_offset_y))
    else:
        screen.blit(pressure_cooker_high, (300 + shake_offset_x, 200 + shake_offset_y))

def draw_start_button():
    button_rect = pygame.Rect(10, 100, 150, 50)
    pygame.draw.rect(screen, GREEN if not automatic_mode else RED, button_rect)
    text = font.render("Start" if not automatic_mode else "Stop", True, BLACK)
    screen.blit(text, (button_rect.x + 20, button_rect.y + 10))

def draw_slider():
    pygame.draw.rect(screen, BLACK, (slider_x, slider_y, slider_width, slider_height))
    slider_handle_x = slider_x + (temperature / 300) * slider_width
    pygame.draw.circle(screen, GREEN, (int(slider_handle_x), slider_y + slider_height // 2), slider_handle_radius)

def draw_scales():
    for i, (label, value) in enumerate([("Weight", weight), ("Thickness", thickness), ("Water Level", water_level)]):
        pygame.draw.rect(screen, BLACK, (scales_x + i * 220, scales_y, 200, slider_height))
        handle_pos = scales_x + i * 220 + (value / 100) * 200
        pygame.draw.circle(screen, GREEN, (int(handle_pos), scales_y + slider_height // 2), slider_handle_radius)
        label_text = font.render(label, True, BLACK)
        screen.blit(label_text, (scales_x + i * 220 + 10, scales_y - 30))

def draw_popup():
    popup_rect = pygame.Rect(200, 150, 400, 200)
    pygame.draw.rect(screen, WHITE, popup_rect)
    pygame.draw.rect(screen, BLACK, popup_rect, 5)
    
    message = font.render("Can you take me out here?", True, BLACK)
    screen.blit(message, (popup_rect.x + 50, popup_rect.y + 50))

    yes_button = pygame.Rect(popup_rect.x + 50, popup_rect.y + 120, 100, 50)
    pygame.draw.rect(screen, GREEN, yes_button)
    yes_text = font.render("Yes", True, BLACK)
    screen.blit(yes_text, (yes_button.x + 30, yes_button.y + 10))

    no_button = pygame.Rect(popup_rect.x + 250, popup_rect.y + 120, 100, 50)
    pygame.draw.rect(screen, RED, no_button)
    no_text = font.render("No", True, BLACK)
    screen.blit(no_text, (no_button.x + 30, no_button.y + 10))

    return yes_button, no_button

clock = pygame.time.Clock()
running = True

while running:
    screen.blit(background_image, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if not show_popup and 10 <= mouse_pos[0] <= 160 and 100 <= mouse_pos[1] <= 150:
                if automatic_mode:
                    decrease_mode = True
                    decrease_timer = pygame.time.get_ticks()
                    automatic_mode = False
                else:
                    automatic_mode = True
                    temperature = fuzzy_inference(weight, thickness, water_level)
                    pressure_level = calculate_pressure(temperature)
                    increase_temperature = True
                    last_time = pygame.time.get_ticks()

            if show_popup:
                yes_button, no_button = draw_popup()
                if yes_button.collidepoint(mouse_pos):
                    remove_cooker = True
                    show_popup = False
                elif no_button.collidepoint(mouse_pos):
                    show_popup = False

            if slider_x <= mouse_pos[0] <= slider_x + slider_width and slider_y <= mouse_pos[1] <= slider_y + slider_height:
                temperature = (mouse_pos[0] - slider_x) / slider_width * 300
                temperature = max(0, min(temperature, 300))
                pressure_level = calculate_pressure(temperature)

            for i, (var_name, var_value) in enumerate([("weight", weight), ("thickness", thickness), ("water_level", water_level)]):
                if scales_x + i * 220 <= mouse_pos[0] <= scales_x + i * 220 + 200 and scales_y <= mouse_pos[1] <= scales_y + slider_height:
                    new_value = (mouse_pos[0] - (scales_x + i * 220)) / 200 * 100
                    new_value = max(0, min(new_value, 100))
                    if var_name == "weight":
                        weight = new_value
                    elif var_name == "thickness":
                        thickness = new_value
                    elif var_name == "water_level":
                        water_level = new_value

                    temperature = fuzzy_inference(weight, thickness, water_level)
                    pressure_level = calculate_pressure(temperature)

    if automatic_mode and increase_temperature:
        current_time = pygame.time.get_ticks()
        if current_time - last_time > 1000:
            if temperature < 300:
                temperature += 5
                pressure_level = calculate_pressure(temperature)
            last_time = current_time

    if decrease_mode:
        current_time = pygame.time.get_ticks()
        if current_time - decrease_timer >= decrease_interval:
            if temperature > 0:
                temperature -= decrease_amount
                pressure_level = calculate_pressure(temperature)
            decrease_timer = current_time  

    draw_pressure_cooker(pressure_level)
    draw_start_button()
    draw_slider()
    draw_scales()

    temperature_text = font.render(f"Temperature: {temperature:.1f}", True, BLACK)
    pressure_text = font.render(f"Pressure Level: {pressure_level}", True, BLACK)
    screen.blit(temperature_text, (10, 10))
    screen.blit(pressure_text, (10, 40))

    if show_popup:
        draw_popup()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()