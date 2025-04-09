let scene, camera, renderer, nodes = [], links = [];
const NODE_SIZE = 2;
const SPACE_RADIUS = 100;

function initBlockchainViz(containerId) {
    // Setup scene
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth * 0.8, window.innerHeight * 0.6);
    document.getElementById(containerId).appendChild(renderer.domElement);

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);

    // Add directional light
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(10, 10, 10);
    scene.add(light);

    // Position camera
    camera.position.z = 150;

    // Add controls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Start animation
    animate();
}

function addBlock(blockData) {
    // Create sphere for node
    const geometry = new THREE.SphereGeometry(NODE_SIZE, 32, 32);
    const material = new THREE.MeshPhongMaterial({
        color: blockData.transaction_type === 'IN' ? 0x00ff00 : 0xff0000,
        transparent: true,
        opacity: 0.8
    });
    const node = new THREE.Mesh(geometry, material);

    // Position on sphere surface
    const phi = Math.acos(-1 + (2 * nodes.length) / 50);
    const theta = Math.sqrt(50 * Math.PI) * phi;
    node.position.x = SPACE_RADIUS * Math.cos(theta) * Math.sin(phi);
    node.position.y = SPACE_RADIUS * Math.sin(theta) * Math.sin(phi);
    node.position.z = SPACE_RADIUS * Math.cos(phi);

    // Add to scene
    scene.add(node);
    nodes.push({
        mesh: node,
        data: blockData
    });

    // Add link to previous block
    if (nodes.length > 1) {
        const prevNode = nodes[nodes.length - 2];
        const linkGeometry = new THREE.BufferGeometry().setFromPoints([
            node.position,
            prevNode.mesh.position
        ]);
        const linkMaterial = new THREE.LineBasicMaterial({
            color: 0x0088ff,
            transparent: true,
            opacity: 0.3
        });
        const link = new THREE.Line(linkGeometry, linkMaterial);
        scene.add(link);
        links.push(link);
    }
}

function animate() {
    requestAnimationFrame(animate);

    // Rotate nodes
    nodes.forEach(node => {
        node.mesh.rotation.x += 0.01;
        node.mesh.rotation.y += 0.01;
    });

    // Move camera in circular motion
    const time = Date.now() * 0.0005;
    camera.position.x = Math.cos(time) * 200;
    camera.position.z = Math.sin(time) * 200;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
}

function updateBlockchainViz(blocks) {
    // Clear existing nodes and links
    nodes.forEach(node => scene.remove(node.mesh));
    links.forEach(link => scene.remove(link));
    nodes = [];
    links = [];

    // Add new blocks
    blocks.forEach(block => addBlock(block));
}
