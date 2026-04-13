import * as THREE from "three";

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// castle floor
const geometry = new THREE.BoxGeometry(20,1,20);
const material = new THREE.MeshStandardMaterial({color:0x555555});
const floor = new THREE.Mesh(geometry, material);
scene.add(floor);

camera.position.z = 10;

function animate(){
 requestAnimationFrame(animate);
 renderer.render(scene, camera);
}

animate();