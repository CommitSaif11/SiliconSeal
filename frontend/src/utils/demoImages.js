const DEMO_ICS = [
  {
    name: 'STM32F030C8T6.png',
    lines: ['STM32F030C8T6', '2347', 'A3B5C', 'ST'],
    bg: [40, 40, 45],
    fg: [220, 220, 215],
  },
  {
    name: 'STM32F407ZET6.png',
    lines: ['STM32F407ZET6', '2512', 'PHL K7M2', 'ST'],
    bg: [35, 35, 40],
    fg: [210, 210, 205],
  },
  {
    name: 'ATMEGA328P.png',
    lines: ['ATMEGA328P', '2248', 'U1834', 'MICROCHIP'],
    bg: [30, 30, 35],
    fg: [200, 200, 195],
  },
  {
    name: 'INA219.png',
    lines: ['INA219', 'AIDR', '2441', 'TI'],
    bg: [25, 25, 30],
    fg: [215, 215, 210],
  },
  {
    name: 'STM32H753ZIT6.png',
    lines: ['STM32H753ZIT6', '2503', 'GH VQ', 'ST'],
    bg: [38, 38, 42],
    fg: [225, 225, 220],
  },
];

function generateICImage({ lines, bg, fg }) {
  const canvas = document.createElement('canvas');
  const w = 400;
  const h = 240;
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');

  // IC body
  ctx.fillStyle = `rgb(${bg[0]}, ${bg[1]}, ${bg[2]})`;
  ctx.beginPath();
  ctx.roundRect(10, 10, w - 20, h - 20, 8);
  ctx.fill();

  // Subtle edge bevel
  ctx.strokeStyle = `rgba(255,255,255,0.08)`;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(10, 10, w - 20, h - 20, 8);
  ctx.stroke();

  // Pin 1 marker
  ctx.fillStyle = `rgba(255,255,255,0.25)`;
  ctx.beginPath();
  ctx.arc(30, 30, 5, 0, Math.PI * 2);
  ctx.fill();

  // IC text
  ctx.fillStyle = `rgb(${fg[0]}, ${fg[1]}, ${fg[2]})`;
  ctx.textAlign = 'left';

  const fontSizes = [22, 16, 16, 14];
  const startY = 70;
  const lineSpacing = 38;

  lines.forEach((text, i) => {
    const size = fontSizes[i] || 14;
    ctx.font = `600 ${size}px 'JetBrains Mono', 'Courier New', monospace`;
    // slight random offset for realism
    const xOffset = 40 + Math.sin(i * 1.7) * 3;
    ctx.fillText(text, xOffset, startY + i * lineSpacing);
  });

  // Pins on sides
  ctx.fillStyle = `rgb(180, 180, 175)`;
  for (let i = 0; i < 12; i++) {
    const y = 25 + i * (h - 50) / 11;
    ctx.fillRect(0, y - 2, 12, 4);
    ctx.fillRect(w - 12, y - 2, 12, 4);
  }
  for (let i = 0; i < 8; i++) {
    const x = 35 + i * (w - 70) / 7;
    ctx.fillRect(x - 2, 0, 4, 12);
    ctx.fillRect(x - 2, h - 12, 4, 12);
  }

  return canvas;
}

function canvasToFile(canvas, filename) {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve(new File([blob], filename, { type: 'image/png' }));
    }, 'image/png');
  });
}

export async function generateDemoFile(index = 0) {
  const ic = DEMO_ICS[index % DEMO_ICS.length];
  const canvas = generateICImage(ic);
  return canvasToFile(canvas, ic.name);
}

export async function generateAllDemoFiles() {
  return Promise.all(DEMO_ICS.map((ic, i) => {
    const canvas = generateICImage(ic);
    return canvasToFile(canvas, ic.name);
  }));
}

export function getDemoPreviewUrl(index = 0) {
  const ic = DEMO_ICS[index % DEMO_ICS.length];
  const canvas = generateICImage(ic);
  return canvas.toDataURL('image/png');
}

export const DEMO_COUNT = DEMO_ICS.length;
export const DEMO_NAMES = DEMO_ICS.map((ic) => ic.name);
