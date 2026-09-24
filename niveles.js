// Los cinco cuartos. Cada cuarto mide LARGO px; el piso está en y = 184.
// cosas: [nombre, x] o [nombre, x, tipo]. El nombre dice de dónde sale el dibujo:
//        "p:xxx"  de las hojas de cada cuarto (escenarios/piezas.json, hecho por recortar_hojas.py; algunos muebles
//                 redibujados de frente o de lado en muebles.py)
//        "o:xxx"  de los dibujados por código (escenarios/objetos.json)
//        "xxx"    de las primeras hojas (escenarios/cosas.json): hongos y charco
//        Lo que hace cada una lo dice su tipo: plataforma, rebote, peligro, charco o adorno.
//        No llevan altura: cada una cae sobre lo que tenga debajo (el piso o una cosa anterior de la lista),
//        así que para apilar se pone primero la de abajo.
//        Pocas cosas y solo las típicas de cada lugar (pedido de la dueña): que no se sature.
// enemigos: [nombre, x desde donde anda, cuántos px va y vuelve, alto (solo la polilla, que vuela)]
//           Uno o dos tipos por cuarto (ver ENEMIGO en juego.js).
// monedas: [x, alto, cuántas en fila]   estrellas: [x, alto]   tesoro: [nombre, x, alto]
// npc: [personaje, animación, x] (no sale si es el que se está jugando)
'use strict';
const LARGO = 2304;
const NIVELES = {
  patio: {
    nombre: 'El patio', musica: 'patio', hundir: 2,
    cosas: [
      ['p:lena', 150], ['o:mata1', 250], ['hongo', 480], ['o:mata3', 540], ['p:trampa', 690], ['p:lena', 745], ['p:parrilla', 850],
      ['charco', 960], ['p:bananos_canasta', 1040], ['o:mata1', 1095], ['p:banca', 1250], ['p:silla_patio', 1385], ['p:lena', 1440],
      ['o:cactus', 1530], ['p:heliconia', 1620, 'adorno'], ['hongo', 1780], ['o:mata3', 1840], ['p:gnomo', 2020],
    ],
    enemigos: [['caracol', 620, 60], ['saltamontes', 1150, 100], ['caracol', 1700, 50], ['saltamontes', 1930, 70]],
    monedas: [[170, 70, 3], [250, 100, 3], [540, 160, 3], [800, 100, 3], [1040, 85, 3], [1100, 88, 3], [1270, 100, 4], [1460, 80, 3], [1620, 70, 3], [1840, 160, 3]],
    estrellas: [[190, 80], [265, 100], [560, 170], [820, 100], [1060, 90], [1120, 92], [1300, 120], [1860, 170]],
    tesoro: ['llave', 2030, 100],
    npc: [['keylin', 'pose', 2195]],
  },
  cocina: {
    nombre: 'La cocina', musica: 'cocina', hundir: 9,
    cosas: [
      ['p:hierbas', 90, 'adorno'],
      ['p:olla', 180], ['p:tortillas', 380], ['p:molinillo', 460], ['p:cafe_britt', 520], ['p:taza_cr', 720],
      ['charco', 840], ['p:gallo_pinto', 1010], ['p:bananos', 1250], ['p:salero', 1400], ['p:olla', 1460],
      ['p:lizano', 1680], ['p:tarrina', 1900],
    ],
    enemigos: [['gorgojo', 270, 90], ['gorgojo', 1100, 130], ['gorgojo', 1760, 120]],
    monedas: [[180, 80, 3], [380, 80, 3], [460, 110, 3], [700, 85, 3], [950, 40, 3], [1250, 90, 3], [1460, 95, 3], [1670, 90, 3], [1900, 70, 3]],
    estrellas: [[205, 95], [400, 85], [535, 115], [715, 90], [1025, 95], [1265, 90], [1695, 95], [2065, 40]],
    tesoro: ['brujula', 1480, 120],
    npc: [],
  },
  sala: {
    nombre: 'La sala', musica: 'sala', hundir: 8,
    cosas: [
      ['p:vasija', 160], ['p:taburete', 210], ['p:mesa_redonda', 290], ['p:cojines', 520], ['p:radio', 700],
      ['p:maceta_sala', 800], ['p:trampa', 920], ['p:bola', 1060], ['p:taburete', 1150], ['p:mesa_redonda', 1230],
      ['p:cojines', 1480], ['p:libros', 1700], ['p:taburete', 1760], ['p:mesa_redonda', 1840], ['p:paraguero', 2060, 'adorno'],
    ],
    enemigos: [['polilla', 560, 220, 80], ['polilla', 1300, 250, 100], ['polilla', 1900, 200, 90]],
    monedas: [[160, 50, 2], [290, 110, 4], [520, 130, 3], [700, 70, 3], [1150, 80, 3], [1240, 110, 4], [1480, 150, 3], [1760, 80, 3], [1850, 110, 4]],
    estrellas: [[340, 120], [560, 110], [720, 70], [830, 110], [1060, 60], [1280, 120], [1520, 120], [1880, 120]],
    tesoro: ['reloj', 1500, 165],
    npc: [['maritza', 'sentada', 1625]],
  },
  cuarto: {
    nombre: 'El cuarto', musica: 'cuarto', hundir: 11,
    cosas: [
      ['p:silla_roja', 150], ['p:comoda', 190], ['p:mochila', 360], ['p:baul', 420], ['p:radio', 440], ['p:trampa', 600],
      ['p:silla_azul', 700], ['p:comoda', 736], ['p:orquidea', 756], ['p:libros', 990], ['p:mochila', 1150], ['p:baul', 1200],
      ['p:silla_morada', 1560], ['p:comoda', 1600], ['p:radio', 1615], ['p:canasta', 1850], ['p:baul', 1900],
    ],
    enemigos: [['oruga', 290, 50], ['oruga', 1300, 90], ['oruga', 1720, 90]],
    monedas: [[150, 60, 2], [360, 70, 2], [420, 90, 3], [700, 55, 3], [740, 95, 3], [990, 85, 2], [1200, 95, 3], [1600, 95, 3], [1900, 95, 3]],
    estrellas: [[225, 95], [440, 140], [700, 60], [775, 140], [1000, 85], [1220, 95], [1630, 140], [1920, 95]],
    tesoro: ['mapa', 1640, 150],
    npc: [],
  },
  bano: {
    nombre: 'El baño', musica: 'bano', hundir: 8,
    cosas: [
      ['p:jabon_soap', 150], ['p:clover', 215], ['p:clorox', 265], ['charco', 400], ['p:balde', 520], ['p:suavitel', 590],
      ['p:protex', 760], ['charco', 860], ['p:rexona', 980], ['p:ariel', 1060], ['p:zest', 1250], ['p:zest', 1255],
      ['p:meneito', 1320], ['p:panuelos', 1650], ['p:fabuloso', 1710], ['p:jabon_soap', 1950],
    ],
    enemigos: [['rana', 350, 120], ['rana', 1150, 90], ['rana', 1800, 100]],
    monedas: [[150, 50, 3], [265, 100, 2], [520, 85, 3], [590, 110, 2], [760, 80, 3], [980, 90, 3], [1250, 80, 3], [1650, 70, 3], [1950, 50, 3]],
    estrellas: [[240, 110], [330, 40], [550, 90], [610, 110], [1000, 100], [1080, 110], [1340, 115], [1730, 110]],
    tesoro: ['canica', 1335, 135],
    npc: [],
  },
};
const ORDEN = ['patio', 'cocina', 'sala', 'cuarto', 'bano'];
