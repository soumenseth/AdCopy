from flask import Flask, render_template, request, redirect, url_for
from ad import app
import os
from ad.utils import *
from ad.path import *


@app.route('/')
@app.route('/home')
def home_page():
    product_filenames = os.listdir(IMAGES_DIR)
    image_paths = ['images/' + pf for pf in product_filenames]
    return render_template('home.html', image_paths=image_paths)


@app.route('/processing')
def processing_page():
    logo_filenames = os.listdir(LOGO_DIR)

    logos = []
    for i, fname in enumerate(logo_filenames):
        name = 'flexRadioLogo'
        id = 'flexRadioLogo' + str(i)
        filename = 'logo/' + fname
        logos.append({'id': id, 'name': name, 'filename': filename})
    return render_template('processing.html', logos=logos, selected_image=False)


@app.route('/processing', methods=['POST'])
def select_image():
    selected_image = request.form['home-image']
    logo_filenames = os.listdir(LOGO_DIR)
    cta_filenames = os.listdir(CTA_DIR)
    shoe_filenames = os.listdir(SHOES_DIR)

    logos = []
    for i, fname in enumerate(logo_filenames):
        name = 'flexRadioLogo'
        id = 'flexRadioLogo' + str(i)
        filename = 'logo/' + fname
        logos.append({'id': id, 'name': name, 'filename': filename})

    ctas = []
    for i, fname in enumerate(cta_filenames):
        name = 'flexRadioCTA'
        id = 'flexRadioCTA' + str(i)
        filename = 'cta/' + fname
        ctas.append({'id': id, 'name': name, 'filename': filename})

    shoes = []
    for i, fname in enumerate(shoe_filenames):
        name = 'flexRadioShoes'
        id = 'flexRadioShoes' + str(i)
        filename = 'shoes/' + fname
        shoes.append({'id': id, 'name': name, 'filename': filename})

    enhancements = read_json(ENHANCEMENTS_PATH)
    filters = read_json(FILTERS_PATH)
    return render_template('processing.html',
                           logos=logos, ctas=ctas,
                           shoes=shoes, filters=filters,
                           enhancements=enhancements,
                           selected_image=selected_image)


@app.route('/submit', methods=['POST'])
def submit():
    path_shoe = request.form['flexRadioShoes']
    selected_logo = request.form['flexRadioLogo']
    selected_cta = request.form['flexRadioCTA']
    selected_enhancement = request.form['flexRadioEnhance']
    selected_filter = request.form['flexRadioFilter']
    message = request.form['textmessage']

    generate_output_image(path_background=request.form['bg_image'],
                          path_logo=request.form['flexRadioLogo'],
                          path_cta=request.form['flexRadioCTA'],
                          path_shoe=request.form['flexRadioShoes'],
                          enhancement_type=request.form['flexRadioEnhance'],
                          filter_type=request.form['flexRadioFilter'],
                          message=request.form['textmessage'])

    return redirect(url_for('output_page'))


@app.route('/')
@app.route('/output')
def output_page():
    product_filenames = os.listdir('ad/static/images')
    image_paths = ['images/' + pf for pf in product_filenames]
    return render_template('home.html', image_path=image_paths[0])
