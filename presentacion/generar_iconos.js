// Genera los íconos PNG (256 px) de presentacion/assets/iconos a partir de react-icons (Font Awesome 6).
// Uso: npm install react-icons react react-dom sharp && node presentacion/generar_iconos.js
const path = require('path');
const React = require('react'), R = require('react-dom/server'), sharp = require('sharp'), fa = require('react-icons/fa6');
const ICONOS = {
  map: 'FaMapLocationDot', helmet: 'FaHelmetSafety', ruler: 'FaCompassDrafting', truck: 'FaTruckFast',
  clip: 'FaClipboardList', users: 'FaUsers', wrench: 'FaWrench', clock: 'FaClock', check: 'FaCircleCheck',
  search: 'FaMagnifyingGlass', usercheck: 'FaUserCheck', unlock: 'FaUnlock', flag: 'FaFlagCheckered',
  layers: 'FaLayerGroup', industry: 'FaIndustry', xmark: 'FaCircleXmark', chart: 'FaChartLine',
  target: 'FaBullseye', book: 'FaBook', contract: 'FaFileContract', handshake: 'FaHandshake',
  laptop: 'FaLaptop', cube: 'FaCube', sitemap: 'FaSitemap', calendar: 'FaCalendarDays', boxes: 'FaBoxesStacked',
  warning: 'FaTriangleExclamation', shield: 'FaShieldHalved', gears: 'FaGears', teach: 'FaPersonChalkboard',
  comments: 'FaComments', database: 'FaDatabase', cloud: 'FaCloud', barcode: 'FaBarcode', road: 'FaRoad',
  bolt: 'FaBolt', listcheck: 'FaListCheck', cycle: 'FaArrowsRotate', stairs: 'FaStairs', scale: 'FaScaleBalanced',
  bulb: 'FaLightbulb', grad: 'FaGraduationCap', hourglass: 'FaHourglassHalf', usertie: 'FaUserTie',
  digging: 'FaPersonDigging', warehouse: 'FaWarehouse', filter: 'FaFilter', eye: 'FaEye', penruler: 'FaPenRuler',
  file: 'FaFileLines', clipcheck: 'FaClipboardCheck', rocket: 'FaRocket', puzzle: 'FaPuzzlePiece',
  seedling: 'FaSeedling', walk: 'FaPersonWalking', run: 'FaPersonRunning', baby: 'FaBaby', ban: 'FaBan',
  star: 'FaStar', key: 'FaKey', plug: 'FaPlug', compass: 'FaCompass', question: 'FaCircleQuestion',
  percent: 'FaPercent', calculator: 'FaCalculator', stopwatch: 'FaStopwatch', folder: 'FaFolderOpen',
  cubes: 'FaCubes', project: 'FaDiagramProject', group: 'FaPeopleGroup', building: 'FaBuilding', user: 'FaUser',
  link: 'FaLink', gauge: 'FaGauge', route: 'FaRoute', money: 'FaMoneyBillTrendUp', thumbsup: 'FaThumbsUp',
  lock: 'FaLock', signs: 'FaSignsPost', trophy: 'FaTrophy', quote: 'FaQuoteLeft', hammer: 'FaHammer',
  sun: 'FaSun', crane: 'FaTrowelBricks', box: 'FaBoxOpen', ship: 'FaShip', play: 'FaCirclePlay', water: 'FaWater',
};
const COLORES = { w: '#FFFFFF', o: '#FF6600', d: '#1A1A1A', b: '#003087', g: '#6D6E71' };
const SALIDA = path.join(__dirname, 'assets', 'iconos');
(async () => {
  for (const [k, n] of Object.entries(ICONOS)) {
    if (!fa[n]) { console.log('falta', n); continue; }
    for (const [ck, c] of Object.entries(COLORES)) {
      const svg = R.renderToStaticMarkup(React.createElement(fa[n], { color: c, size: 256 }));
      await sharp(Buffer.from(svg)).resize(256, 256, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .png({ compressionLevel: 9 }).toFile(path.join(SALIDA, `${k}_${ck}.png`));
    }
  }
  console.log('listo');
})();
