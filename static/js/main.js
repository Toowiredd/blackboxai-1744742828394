import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import io from 'socket.io-client';

const socket = io.connect('http://localhost:5000');

let scene, camera, renderer, controls;
let buttons = {};

init();
animate();

function init() {
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);

    // Camera setup
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.6, 3);

    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // OrbitControls setup
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.screenSpacePanning = false;
    controls.maxPolarAngle = Math.PI / 2;

    // Load 3D model
    const loader = new GLTFLoader();
    loader.load('/path/to/model.glb', (gltf) => {
        scene.add(gltf.scene);
    });

    // Add event listeners
    window.addEventListener('resize', onWindowResize, false);

    // Listen for button state updates from the server
    socket.on('button_config_updated', (data) => {
        console.log('Button config updated:', data);
        updateButtonState(data);
    });

    // Example button creation
    createButton('exampleButton', { x: 0, y: 1, z: 0 }, { x: 0, y: 0, z: 0 }, 1);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function createButton(id, position, rotation, scale) {
    const geometry = new THREE.BoxGeometry();
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const button = new THREE.Mesh(geometry, material);
    button.position.set(position.x, position.y, position.z);
    button.rotation.set(rotation.x, rotation.y, rotation.z);
    button.scale.set(scale, scale, scale);
    button.userData.id = id;
    scene.add(button);
    buttons[id] = button;

    // Add interaction event listeners
    button.addEventListener('click', () => {
        emitButtonInteraction(id, 'click');
    });
}

function updateButtonState(data) {
    const button = buttons[data.id];
    if (button) {
        button.position.set(data.position.x, data.position.y, data.position.z);
        button.rotation.set(data.rotation.x, data.rotation.y, data.rotation.z);
        button.scale.set(data.scale, data.scale, data.scale);
    }
}

function emitButtonInteraction(buttonId, interactionType) {
    socket.emit('button_interaction', {
        button_id: buttonId,
        type: interactionType
    });
}

// UI/UX improvements
function addPresets() {
    // Add preset buttons or configurations
}

function addTooltips() {
    // Add tooltips to buttons or UI elements
}

function addOnboardingTutorials() {
    // Add onboarding tutorials for new users
}

// Call UI/UX improvement functions
addPresets();
addTooltips();
addOnboardingTutorials();
