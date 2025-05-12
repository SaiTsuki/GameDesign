// script.js (Версия с отладкой pitch)

const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');

// --- Configuration ---
const MAZE_WIDTH = 15;
const MAZE_HEIGHT = 15;
const MAZE_DEPTH = 15;
const CELL_SIZE = 1.0;

const RENDER_RESOLUTION_FACTOR = 0.5;
let canvasWidth = window.innerWidth;
let canvasHeight = window.innerHeight;
canvas.width = Math.max(1, Math.floor(canvasWidth * RENDER_RESOLUTION_FACTOR));
canvas.height = Math.max(1, Math.floor(canvasHeight * RENDER_RESOLUTION_FACTOR));
canvas.style.width = `${canvasWidth}px`;
canvas.style.height = `${canvasHeight}px`;

const MOVE_SPEED = 0.1;
const ROTATION_SPEED = 0.05; // Можно попробовать увеличить (e.g., 0.1)
const FOV = Math.PI / 3;
const MAX_RAY_DISTANCE = 25.0;
const PLAYER_RADIUS = 0.25;

// --- State ---
let camera = {
    x: MAZE_WIDTH / 2 * CELL_SIZE,
    y: MAZE_HEIGHT / 2 * CELL_SIZE,
    z: MAZE_DEPTH / 2 * CELL_SIZE,
    yaw: 0,
    pitch: 0, // Значение наклона, которое должно меняться
};

let keysPressed = {};
let maze = [];

// --- Helper: Pseudo-Random Number Generation (unchanged) ---
function simpleHash(x, y, z) {
    let ix = Math.floor(x * 100); let iy = Math.floor(y * 100); let iz = Math.floor(z * 100);
    let seed = (ix * 31337 + iy * 1013 + iz * 4261) & 0x7FFFFFFF;
    seed = (seed ^ (seed >> 15)) * 1103515245; seed = (seed ^ (seed >> 13)) * 1103515245; seed = (seed ^ (seed >> 16)) & 0x7FFFFFFF;
    return seed;
}
function seededRandom(seed) {
    let nextSeed = (1103515245 * seed + 12345) & 0x7FFFFFFF;
    let randomValue = nextSeed / 0x80000000;
    return { value: randomValue, nextSeed: nextSeed };
}
function getStableNoiseColor(hitX, hitY, hitZ, distance) {
    let currentSeed = simpleHash(hitX, hitY, hitZ);
    let rand1 = seededRandom(currentSeed); let rand2 = seededRandom(rand1.nextSeed); let rand3 = seededRandom(rand2.nextSeed);
    const rBase = Math.floor(rand1.value * 200 + 55); const gBase = Math.floor(rand2.value * 200 + 55); const bBase = Math.floor(rand3.value * 200 + 55);
    const brightness = Math.max(0, 1.0 - (distance / MAX_RAY_DISTANCE) * 0.95);
    const shimmer = 1.0;
    const r = rBase * brightness * shimmer; const g = gBase * brightness * shimmer; const b = bBase * brightness * shimmer;
    return [r, g, b];
}

// --- Maze Generation (unchanged) ---
function initializeMaze(){ /*...*/ maze = Array.from({ length: MAZE_WIDTH }, () => Array.from({ length: MAZE_HEIGHT }, () => new Array(MAZE_DEPTH).fill(1))); }
function isValid(x, y, z){ /*...*/ return x >= 0 && x < MAZE_WIDTH && y >= 0 && y < MAZE_HEIGHT && z >= 0 && z < MAZE_DEPTH; }
function generateMazeRecursive(cx, cy, cz){ maze[cx][cy][cz] = 0; const directions = [ { dx: 1, dy: 0, dz: 0 }, { dx: -1, dy: 0, dz: 0 }, { dx: 0, dy: 1, dz: 0 }, { dx: 0, dy: -1, dz: 0 }, { dx: 0, dy: 0, dz: 1 }, { dx: 0, dy: 0, dz: -1 } ]; for (let i = directions.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [directions[i], directions[j]] = [directions[j], directions[i]]; } for (const dir of directions) { const nx = cx + dir.dx * 2; const ny = cy + dir.dy * 2; const nz = cz + dir.dz * 2; if (isValid(nx, ny, nz) && maze[nx][ny][nz] === 1) { maze[cx + dir.dx][cy + dir.dy][cz + dir.dz] = 0; generateMazeRecursive(nx, ny, nz); } } }
function generateMaze(){ console.log("Generating 3D maze..."); initializeMaze(); const startX = Math.floor(Math.random()*(MAZE_WIDTH/2))*2+1; const startY = Math.floor(Math.random()*(MAZE_HEIGHT/2))*2+1; const startZ = Math.floor(Math.random()*(MAZE_DEPTH/2))*2+1; const clampedStartX = Math.min(startX, MAZE_WIDTH - (MAZE_WIDTH % 2 === 0 ? 2 : 1)); const clampedStartY = Math.min(startY, MAZE_HEIGHT - (MAZE_HEIGHT % 2 === 0 ? 2 : 1)); const clampedStartZ = Math.min(startZ, MAZE_DEPTH - (MAZE_DEPTH % 2 === 0 ? 2 : 1)); if(isValid(clampedStartX, clampedStartY, clampedStartZ)){ generateMazeRecursive(clampedStartX, clampedStartY, clampedStartZ); if(maze[clampedStartX][clampedStartY][clampedStartZ] === 0){ camera.x = (clampedStartX + 0.5) * CELL_SIZE; camera.y = (clampedStartY + 0.5) * CELL_SIZE; camera.z = (clampedStartZ + 0.5) * CELL_SIZE; }else{ console.warn("Maze generation start point was a wall? Falling back."); outerLoop: for (let y = 1; y < MAZE_HEIGHT - 1; y++) for (let x = 1; x < MAZE_WIDTH - 1; x++) for (let z = 1; z < MAZE_DEPTH - 1; z++) if (maze[x][y][z] === 0) { camera.x = (x + 0.5) * CELL_SIZE; camera.y = (y + 0.5) * CELL_SIZE; camera.z = (z + 0.5) * CELL_SIZE; break outerLoop; } } }else{ console.error("Could not find valid start point."); camera.x = 1.5 * CELL_SIZE; camera.y = 1.5 * CELL_SIZE; camera.z = 1.5 * CELL_SIZE; } console.log("Maze generated."); for(let y=0; y<MAZE_HEIGHT; ++y) for(let x=0; x<MAZE_WIDTH; ++x) { maze[x][y][0] = 1; maze[x][y][MAZE_DEPTH-1] = 1; } for(let y=0; y<MAZE_HEIGHT; ++y) for(let z=0; z<MAZE_DEPTH; ++z) { maze[0][y][z] = 1; maze[MAZE_WIDTH-1][y][z] = 1; } for(let x=0; x<MAZE_WIDTH; ++x) for(let z=0; z<MAZE_DEPTH; ++z) { maze[x][0][z] = 1; maze[x][MAZE_HEIGHT-1][z] = 1; } }


// --- Input Handling (unchanged) ---
window.addEventListener('keydown', (e) => {
    keysPressed[e.code] = true;
    if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyQ', 'KeyE'].includes(e.code)) {
        e.preventDefault();
    }
    if (e.code === 'KeyP') { generateAndLogOBJ(); }
});
window.addEventListener('keyup', (e) => { keysPressed[e.code] = false; });

// --- Collision Detection (unchanged) ---
function isWall(worldX, worldY, worldZ){ const mapX = Math.floor(worldX / CELL_SIZE); const mapY = Math.floor(worldY / CELL_SIZE); const mapZ = Math.floor(worldZ / CELL_SIZE); if (!isValid(mapX, mapY, mapZ)) return true; return maze[mapX][mapY][mapZ] === 1; }
function checkCollision(x, y, z){ for (let dx = -PLAYER_RADIUS; dx <= PLAYER_RADIUS; dx += 2 * PLAYER_RADIUS) for (let dy = -PLAYER_RADIUS; dy <= PLAYER_RADIUS; dy += 2 * PLAYER_RADIUS) for (let dz = -PLAYER_RADIUS; dz <= PLAYER_RADIUS; dz += 2 * PLAYER_RADIUS) if (isWall(x + dx, y + dy, z + dz)) return true; return false; }

// --- Update Camera (unchanged logic, verified) ---
function updateCamera() {
    let moveForward = 0;
    let rotateYaw = 0;
    let rotatePitch = 0; // Эта переменная должна получать +1/-1 от Q/E

    if (keysPressed['ArrowUp'] || keysPressed['Space']) moveForward += 1;
    if (keysPressed['ArrowDown']) moveForward -= 1;
    if (keysPressed['KeyA'] || keysPressed['ArrowLeft']) rotateYaw -= 1;
    if (keysPressed['KeyD'] || keysPressed['ArrowRight']) rotateYaw += 1;

    // Проверяем нажатие Q/E
    if (keysPressed['KeyW']) rotatePitch += 1;
    if (keysPressed['KeyS']) rotatePitch -= 1;


    // --- Rotation ---
    camera.yaw += rotateYaw * ROTATION_SPEED;
    // Обновляем pitch - эта строка должна работать
    camera.pitch += rotatePitch * ROTATION_SPEED;
    // Ограничиваем pitch - это не должно полностью блокировать взгляд вверх/вниз
    camera.pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, camera.pitch));

    // --- Movement (uses pitch correctly) ---
    if (moveForward !== 0) {
        const forwardX = Math.sin(camera.yaw) * Math.cos(camera.pitch);
        const forwardY = -Math.sin(camera.pitch); // Использует pitch
        const forwardZ = Math.cos(camera.yaw) * Math.cos(camera.pitch);
        const moveAmount = moveForward * MOVE_SPEED;
        const nextX = camera.x + forwardX * moveAmount;
        const nextY = camera.y + forwardY * moveAmount;
        const nextZ = camera.z + forwardZ * moveAmount;
        if (!checkCollision(nextX, nextY, nextZ)) { camera.x = nextX; camera.y = nextY; camera.z = nextZ; }
        else { if (!checkCollision(nextX, camera.y, nextZ)) { camera.x = nextX; camera.z = nextZ; } else if (!checkCollision(camera.x, nextY, camera.z)) { camera.y = nextY; } }
    }
}


// --- Rendering (uses pitch correctly) ---
let imageData = ctx.createImageData(canvas.width, canvas.height);
let data = imageData.data;

function render() {
    const screenWidth = canvas.width; const screenHeight = canvas.height; const aspectRatio = screenWidth / screenHeight;
    const camX = camera.x, camY = camera.y, camZ = camera.z;
    const sinYaw = Math.sin(camera.yaw), cosYaw = Math.cos(camera.yaw);
    // Используются значения sin/cos от текущего camera.pitch
    const sinPitch = Math.sin(camera.pitch), cosPitch = Math.cos(camera.pitch);

    for (let px = 0; px < screenWidth; px++) {
        for (let py = 0; py < screenHeight; py++) {
            // Calculate ray direction
            const screenX = (2 * px / screenWidth - 1) * aspectRatio; const screenY = 1 - 2 * py / screenHeight;
            const rayDirX_cam = screenX * Math.tan(FOV / 2), rayDirY_cam = screenY * Math.tan(FOV / 2), rayDirZ_cam = 1.0;
            // Применяем поворот по pitch
            let rayDirX_p = rayDirX_cam;
            let rayDirY_p = rayDirY_cam * cosPitch - rayDirZ_cam * sinPitch; // <- Здесь используется pitch
            let rayDirZ_p = rayDirY_cam * sinPitch + rayDirZ_cam * cosPitch; // <- Здесь используется pitch
            // Применяем поворот по yaw
            let rayDirX_w = rayDirX_p * cosYaw + rayDirZ_p * sinYaw, rayDirY_w = rayDirY_p, rayDirZ_w = -rayDirX_p * sinYaw + rayDirZ_p * cosYaw;
            const mag = Math.sqrt(rayDirX_w**2 + rayDirY_w**2 + rayDirZ_w**2);
            if (mag !== 0) { rayDirX_w /= mag; rayDirY_w /= mag; rayDirZ_w /= mag; }

            // Ray Marching
            let distance = MAX_RAY_DISTANCE; let hit = false; const step = 0.05;
            let hitX = 0, hitY = 0, hitZ = 0;
            for (let t = 0; t < MAX_RAY_DISTANCE; t += step) {
                const currentX = camX + rayDirX_w * t; const currentY = camY + rayDirY_w * t; const currentZ = camZ + rayDirZ_w * t;
                const mapX = Math.floor(currentX / CELL_SIZE); const mapY = Math.floor(currentY / CELL_SIZE); const mapZ = Math.floor(currentZ / CELL_SIZE);
                if (!isValid(mapX, mapY, mapZ) || maze[mapX][mapY][mapZ] === 1) {
                    distance = t; hit = true; hitX = currentX; hitY = currentY; hitZ = currentZ; break;
                }
            }

            // Determine Pixel Color
            const pixelIndex = (py * screenWidth + px) * 4; let r = 0, g = 0, b = 0;
            if (hit) { [r, g, b] = getStableNoiseColor(hitX, hitY, hitZ, distance); }
            else { r = 5; g = 5; b = 10; }
            data[pixelIndex] = Math.min(255, Math.max(0, r)); data[pixelIndex + 1] = Math.min(255, Math.max(0, g)); data[pixelIndex + 2] = Math.min(255, Math.max(0, b)); data[pixelIndex + 3] = 255;
        }
    }
    ctx.putImageData(imageData, 0, 0);
}

// --- Maze Export (unchanged) ---
function generateAndLogOBJ(){ /* ... */ console.log("Generating OBJ data... (Copy text below)"); let objData = "# Psychedelic Noise Maze OBJ Export\n"; objData += "# Maze dimensions: " + MAZE_WIDTH + "x" + MAZE_HEIGHT + "x" + MAZE_DEPTH + "\n"; objData += "o MazeMesh\n"; let vertices = []; let faces = []; let vertexIndexMap = {}; let currentVertexIndex = 1; function getVertexIndex(x, y, z) { const key = `${x.toFixed(2)},${y.toFixed(2)},${z.toFixed(2)}`; if (!vertexIndexMap[key]) { vertices.push(`v ${(x * CELL_SIZE).toFixed(4)} ${(y * CELL_SIZE).toFixed(4)} ${(z * CELL_SIZE).toFixed(4)}`); vertexIndexMap[key] = currentVertexIndex++; } return vertexIndexMap[key]; } for (let x = 0; x < MAZE_WIDTH; x++) for (let y = 0; y < MAZE_HEIGHT; y++) for (let z = 0; z < MAZE_DEPTH; z++) if (maze[x][y][z] === 1) { const v = [ [x, y, z], [x + 1, y, z], [x + 1, y + 1, z], [x, y + 1, z], [x, y, z + 1], [x + 1, y, z + 1], [x + 1, y + 1, z + 1], [x, y + 1, z + 1] ]; if (!isValid(x - 1, y, z) || maze[x - 1][y][z] === 0) faces.push(`f ${getVertexIndex(...v[0])} ${getVertexIndex(...v[4])} ${getVertexIndex(...v[7])} ${getVertexIndex(...v[3])}`); if (!isValid(x + 1, y, z) || maze[x + 1][y][z] === 0) faces.push(`f ${getVertexIndex(...v[1])} ${getVertexIndex(...v[2])} ${getVertexIndex(...v[6])} ${getVertexIndex(...v[5])}`); if (!isValid(x, y - 1, z) || maze[x][y - 1][z] === 0) faces.push(`f ${getVertexIndex(...v[0])} ${getVertexIndex(...v[1])} ${getVertexIndex(...v[5])} ${getVertexIndex(...v[4])}`); if (!isValid(x, y + 1, z) || maze[x][y + 1][z] === 0) faces.push(`f ${getVertexIndex(...v[3])} ${getVertexIndex(...v[7])} ${getVertexIndex(...v[6])} ${getVertexIndex(...v[2])}`); if (!isValid(x, y, z - 1) || maze[x][y][z - 1] === 0) faces.push(`f ${getVertexIndex(...v[0])} ${getVertexIndex(...v[3])} ${getVertexIndex(...v[2])} ${getVertexIndex(...v[1])}`); if (!isValid(x, y, z + 1) || maze[x][y][z + 1] === 0) faces.push(`f ${getVertexIndex(...v[4])} ${getVertexIndex(...v[5])} ${getVertexIndex(...v[6])} ${getVertexIndex(...v[7])}`); } objData += "# Vertices (" + vertices.length + ")\n"; objData += vertices.join("\n") + "\n"; objData += "# Faces (" + faces.length + ")\n"; objData += "s 1\n"; objData += faces.join("\n") + "\n"; console.log("--- START OBJ DATA ---"); console.log(objData); console.log("--- END OBJ DATA ---"); alert("OBJ data logged to browser console (Press F12). Copy the text between START and END markers and save as a '.obj' file.");}


// --- Game Loop ---
function gameLoop() {
    updateCamera();
    render();

    requestAnimationFrame(gameLoop);
}

// --- Initialization ---
window.addEventListener('resize', () => {
    canvasWidth = window.innerWidth; canvasHeight = window.innerHeight;
    const newWidth = Math.max(1, Math.floor(canvasWidth * RENDER_RESOLUTION_FACTOR)); const newHeight = Math.max(1, Math.floor(canvasHeight * RENDER_RESOLUTION_FACTOR));
    if (canvas.width !== newWidth || canvas.height !== newHeight) {
        canvas.width = newWidth; canvas.height = newHeight;
        imageData = ctx.createImageData(canvas.width, canvas.height); data = imageData.data;
        console.log(`Canvas resized to: ${canvas.width}x${canvas.height}`);
    }
    canvas.style.width = `${canvasWidth}px`; canvas.style.height = `${canvasHeight}px`;
});

generateMaze();
gameLoop(); // Start the loop
