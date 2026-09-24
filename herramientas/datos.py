"""Junta los .json de sprites, escenarios y objetos en ../datos.js, para que la página abra con
doble clic (desde file:// el navegador no deja leer .json con fetch)."""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
d = {
    'sprites': json.load(open(os.path.join(B, 'sprites', 'sprites.json'), encoding='utf-8')),
    'escenarios': json.load(open(os.path.join(B, 'escenarios', 'escenarios.json'), encoding='utf-8')),
    'objetos': json.load(open(os.path.join(B, 'escenarios', 'objetos.json'), encoding='utf-8')),
    'cosas': json.load(open(os.path.join(B, 'escenarios', 'cosas.json'), encoding='utf-8')),
    'piezas': json.load(open(os.path.join(B, 'escenarios', 'piezas.json'), encoding='utf-8')),
}
with open(os.path.join(B, 'datos.js'), 'w', encoding='utf-8') as f:
    f.write('// Hecho por herramientas/datos.py; no editar a mano.\nwindow.DATOS = ')
    json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
print('datos.js listo')
