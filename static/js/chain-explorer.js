class ChainExplorer {
    constructor(containerId) {
        // Basic setup
        this.container = document.getElementById(containerId);
        this.width = this.container.clientWidth;
        this.height = 600;
        this.nodeRadius = 10;
        
        // Remove any existing loading messages
        const loadingElements = this.container.querySelectorAll('.loading-message');
        loadingElements.forEach(el => el.remove());
        
        // Debug container
        this.debugContainer = document.createElement('div');
        this.debugContainer.className = 'debug-info';
        this.debugContainer.style.cssText = 'position:absolute; top:10px; left:10px; background:rgba(255,255,255,0.9); padding:5px; z-index:9999; border-radius:4px;';
        this.container.appendChild(this.debugContainer);
        
        // Set up THREE.js scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xffffff);
        
        // Camera with wider field of view for spherical display
        this.camera = new THREE.PerspectiveCamera(60, this.width / this.height, 1, 2000);
        this.camera.position.set(0, 0, 600);
        
        // Renderer with antialiasing for smoother edges
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.width, this.height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);
        
        // Add lights for better visual quality
        const ambientLight = new THREE.AmbientLight(0xcccccc, 0.5);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(directionalLight);
        
        // Controls with damping for smoother motion
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // Create object groups
        this.nodeGroup = new THREE.Group();
        
        // Create a main group to hold everything for unified rotation
        this.mainGroup = new THREE.Group();
        this.scene.add(this.mainGroup);
        this.mainGroup.add(this.nodeGroup);
        
        this.linkGroup = new THREE.Group();
        this.mainGroup.add(this.linkGroup);  // Add links to main group instead of scene
        
        // Add connection lines as custom class to handle proper node targeting
        this.LineConnection = class extends THREE.Line {
            constructor(startNode, endNode, options) {
                // Create geometry but will update in refresh
                const geometry = new THREE.BufferGeometry();
                const material = new THREE.LineBasicMaterial(options);
                super(geometry, material);
                
                this.startNode = startNode;
                this.endNode = endNode;
                this.options = options || {};
                this.curveHeight = options.curveHeight || 0;
                
                // Initialize points array for the curve
                this.points = [];
                
                // Initialize connection points
                this.startPoint = new THREE.Vector3();
                this.midPoint = new THREE.Vector3();
                this.endPoint = new THREE.Vector3();
                
                // Initial refresh to set positions
                this.refresh();
            }
            
            refresh() {
                try {
                    // Use exact position vectors to ensure proper connection
                    const startPos = this.startNode.position;
                    const endPos = this.endNode.position;
                    
                    // Get the direction vectors
                    const direction = new THREE.Vector3().subVectors(endPos, startPos).normalize();
                    const reverseDirection = new THREE.Vector3().subVectors(startPos, endPos).normalize();
                    
                    // Get the radius of each node, accounting for scaling
                    const startRadius = this.startNode.geometry.parameters.radius * this.startNode.scale.x;
                    const endRadius = this.endNode.geometry.parameters.radius * this.endNode.scale.x;
                    
                    // Set the start and end points precisely at the node surfaces
                    this.startPoint.copy(startPos).addScaledVector(direction, startRadius);
                    this.endPoint.copy(endPos).addScaledVector(reverseDirection, endRadius);
                    
                    // Calculate midpoint for the curve
                    this.midPoint.copy(this.startPoint).add(this.endPoint).divideScalar(2);
                    
                    // Apply curve perpendicular to the connection line
                    const upVector = new THREE.Vector3(0, 1, 0);
                    let perpendicular = new THREE.Vector3().crossVectors(direction, upVector);
                    
                    // If perpendicular is zero, try another axis
                    if (perpendicular.lengthSq() < 0.001) {
                        perpendicular = new THREE.Vector3().crossVectors(direction, new THREE.Vector3(1, 0, 0));
                    }
                    
                    perpendicular.normalize();
                    
                    // Calculate curve height based on distance
                    const distance = this.startPoint.distanceTo(this.endPoint);
                    const height = distance * this.curveHeight;
                    
                    // Apply offset to midpoint
                    this.midPoint.addScaledVector(perpendicular, height);
                    
                    // Create a quadratic curve
                    const curve = new THREE.QuadraticBezierCurve3(
                        this.startPoint,
                        this.midPoint,
                        this.endPoint
                    );
                    
                    // Generate curve points
                    this.points = curve.getPoints(20);
                    
                    // Update geometry
                    if (this.geometry) this.geometry.dispose();
                    this.geometry = new THREE.BufferGeometry().setFromPoints(this.points);
                } catch (e) {
                    console.error("Error refreshing connection:", e);
                }
            }
        };
        
        // Setup raycaster for interactions
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.hoveredNode = null;
        
        // Create tooltip that will appear on hover
        this.createTooltip();
        
        // Add legend to explain node types
        this.addLegend();
        
        // Mouse event listeners
        this.container.addEventListener('mousemove', this.onMouseMove.bind(this));
        window.addEventListener('resize', this.onWindowResize.bind(this));
        
        // Setup object tracking
        this.nodesById = {};
        
        // Animation loop
        this.animate();
        
        this.updateDebug('Visualization initialized');
    }
    
    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'blockchain-tooltip';
        this.tooltip.style.cssText = `
            position: fixed;
            background: rgba(33, 33, 33, 0.95);
            color: white;
            padding: 12px 15px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.5;
            z-index: 10000;
            max-width: 320px;
            pointer-events: none;
            opacity: 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            backdrop-filter: blur(8px);
            transition: opacity 0.15s ease;
            border-left: 4px solid #2196F3;
        `;
        document.body.appendChild(this.tooltip);
    }
    
    addLegend() {
        const legend = document.createElement('div');
        legend.className = 'blockchain-legend';
        legend.style.cssText = `
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 12px;
        `;
        
        legend.innerHTML = `
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#2196F3;"></span> 
                <span>Donor Node</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#FF5722;"></span> 
                <span>Recipient Node</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="display:inline-block; width:30px; height:2px; background:#aaa;"></span> 
                <span>Fund Flow</span>
            </div>
        `;
        
        this.container.appendChild(legend);
    }
    
    update(data) {
        this.updateDebug(`Processing ${data.length} transactions`);
        
        // Clear previous visualization
        while (this.nodeGroup.children.length > 0) {
            this.nodeGroup.remove(this.nodeGroup.children[0]);
        }
        while (this.linkGroup.children.length > 0) {
            this.linkGroup.remove(this.linkGroup.children[0]);
        }
        this.nodesById = {};
        
        // Extract donors, recipients, and their connections
        const donors = new Map();
        const recipients = new Map();
        const connections = [];
        
        // Process transactions to identify unique donors and recipients
        data.forEach(tx => {
            if (!tx.voucher_code) return;
            
            if (tx.transaction_type === 'IN') {
                // This is a donation
                const donorId = `donor-${tx.voucher_code}`;
                donors.set(donorId, {
                    id: donorId,
                    type: 'donor',
                    name: tx.user || 'Anonymous',
                    amount: parseFloat(tx.amount) || 0,
                    voucher: tx.voucher_code,
                    timestamp: tx.timestamp,
                    tx_id: tx.transaction_id
                });
            } 
            else if (tx.transaction_type === 'OUT' && tx.recipient_id) {
                // This is a disbursement
                const recipientId = `recipient-${tx.recipient_id}`;
                
                if (!recipients.has(recipientId)) {
                    recipients.set(recipientId, {
                        id: recipientId,
                        type: 'recipient',
                        name: tx.user || 'Unknown Recipient',
                        totalReceived: 0,
                        disbursements: []
                    });
                }
                
                const recipient = recipients.get(recipientId);
                recipient.totalReceived += parseFloat(tx.amount) || 0;
                recipient.disbursements.push({
                    amount: parseFloat(tx.amount) || 0,
                    timestamp: tx.timestamp,
                    voucher: tx.voucher_code,
                    tx_id: tx.transaction_id
                });
                
                // Create connection between donor and recipient
                connections.push({
                    source: `donor-${tx.voucher_code}`,
                    target: recipientId,
                    amount: parseFloat(tx.amount) || 0,
                    tx_id: tx.transaction_id
                });
            }
        });
        
        // Create material functions
        const createDonorMaterial = () => new THREE.MeshPhysicalMaterial({
            color: 0x2196F3,
            metalness: 0.2,
            roughness: 0.5,
            clearcoat: 0.8,
            clearcoatRoughness: 0.2,
            transparent: true,
            opacity: 0.85
        });
        
        const createRecipientMaterial = () => new THREE.MeshPhysicalMaterial({
            color: 0xFF5722,
            metalness: 0.2,
            roughness: 0.5,
            clearcoat: 0.8, 
            clearcoatRoughness: 0.2,
            transparent: true,
            opacity: 0.85
        });
        
        // Create donor nodes - distributed in a sphere pattern
        const donorNodes = Array.from(donors.values());
        const nodeSpacing = Math.max(10, 360 / (donorNodes.length || 1));
        
        donorNodes.forEach((donor, i) => {
            // Create sphere for donor
            const geometry = new THREE.SphereGeometry(this.nodeRadius, 24, 24);
            const material = createDonorMaterial();
            const sphere = new THREE.Mesh(geometry, material);
            
            // Position using spherical coordinates
            const phi = Math.acos(-1 + (2 * i) / Math.max(donorNodes.length - 1, 1));
            const theta = Math.sqrt(donorNodes.length * Math.PI) * phi;
            const radius = 200;
            
            sphere.position.x = radius * Math.sin(phi) * Math.cos(theta);
            sphere.position.y = radius * Math.sin(phi) * Math.sin(theta);
            sphere.position.z = radius * Math.cos(phi);
            
            // Store metadata
            sphere.userData = donor;
            
            // Add to scene and tracking
            this.nodeGroup.add(sphere);
            this.nodesById[donor.id] = sphere;
        });
        
        // Create recipient nodes - positioned inside the donor sphere
        const recipientNodes = Array.from(recipients.values());
        recipientNodes.forEach((recipient, i) => {
            // Create larger sphere for recipient
            const geometry = new THREE.SphereGeometry(this.nodeRadius * 1.2, 24, 24);
            const material = createRecipientMaterial();
            const sphere = new THREE.Mesh(geometry, material);
            
            // Position recipients in inner sphere
            const phi = Math.acos(-1 + (2 * i) / Math.max(recipientNodes.length - 1, 1));
            const theta = Math.sqrt(recipientNodes.length * Math.PI) * phi;
            const radius = 100;
            
            sphere.position.x = radius * Math.sin(phi) * Math.cos(theta);
            sphere.position.y = radius * Math.sin(phi) * Math.sin(theta);
            sphere.position.z = radius * Math.cos(theta);
            
            // Add glow effect
            const glowMaterial = new THREE.ShaderMaterial({
                uniforms: {
                    c: { type: "f", value: 0.2 },
                    p: { type: "f", value: 1.7 },
                    glowColor: { type: "c", value: new THREE.Color(0xFF5722) }
                },
                vertexShader: `
                    varying vec3 vNormal;
                    void main() {
                        vNormal = normalize(normalMatrix * normal);
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }
                `,
                fragmentShader: `
                    uniform vec3 glowColor;
                    uniform float c;
                    uniform float p;
                    varying vec3 vNormal;
                    void main() {
                        float intensity = pow(c - dot(vNormal, vec3(0.0, 0.0, 1.0)), p);
                        gl_FragColor = vec4(glowColor, intensity);
                    }
                `,
                side: THREE.BackSide,
                blending: THREE.AdditiveBlending,
                transparent: true
            });
            
            const glowSphere = new THREE.Mesh(
                new THREE.SphereGeometry(this.nodeRadius * 1.6, 24, 24),
                glowMaterial
            );
            sphere.add(glowSphere);
            
            // Store metadata
            sphere.userData = recipient;
            
            // Add to scene and tracking
            this.nodeGroup.add(sphere);
            this.nodesById[recipient.id] = sphere;
        });
        
        // Use the new dedicated method for connections
        this.createConnections(connections);
        
        this.updateDebug(`Created ${donorNodes.length} donors, ${recipientNodes.length} recipients and ${connections.length} connections`);
        
        // Initial animation to spread nodes
        this.performInitialAnimation();
    }
    
    // Add a new method to improve initial positioning
    performInitialAnimation() {
        // Add subtle animation to space out nodes
        let iteration = 0;
        const animatePositions = () => {
            iteration++;
            if (iteration < 60) { // Run for 60 frames
                requestAnimationFrame(animatePositions);
            }
        };
        
        animatePositions();
    }
    
    // Override animate method to handle unified rotation
    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        // Rotate the entire main group instead of just nodes
        this.mainGroup.rotation.y += 0.001;
        
        // Update controls
        this.controls.update();
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
    }
    
    createConnections(connections) {
        connections.forEach(connection => {
            const sourceNode = this.nodesById[connection.source];
            const targetNode = this.nodesById[connection.target];
            
            if (sourceNode && targetNode) {
                try {
                    // Calculate curve height based on amount (more significant curve for larger amounts)
                    const curveHeight = Math.min(0.15, connection.amount * 0.0002);
                    
                    // Create line using the custom LineConnection class
                    const line = new this.LineConnection(sourceNode, targetNode, {
                        color: 0x90A4AE,
                        transparent: true,
                        opacity: 0.8,
                        linewidth: Math.min(3, 1 + connection.amount * 0.005),
                        curveHeight: curveHeight
                    });
                    
                    // Store connection data
                    line.userData = {
                        source: connection.source,
                        target: connection.target,
                        amount: connection.amount,
                        tx_id: connection.tx_id
                    };
                    
                    this.linkGroup.add(line);
                } catch (e) {
                    console.error("Error creating connection:", e);
                }
            }
        });
    }
    
    onMouseMove(event) {
        // Calculate mouse position in normalized device coordinates
        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / this.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / this.height) * 2 + 1;
        
        // Check for intersections
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.nodeGroup.children);
        
        if (intersects.length > 0) {
            const intersectedNode = intersects[0].object;
            
            // Highlight node and show tooltip
            if (this.hoveredNode !== intersectedNode) {
                // Reset previous node and its connections
                if (this.hoveredNode) {
                    this.resetNodeHighlight(this.hoveredNode);
                }
                
                // Highlight new node and its connections
                this.hoveredNode = intersectedNode;
                this.highlightNodeWithConnections(this.hoveredNode);
                
                // Show tooltip
                this.showNodeTooltip(this.hoveredNode.userData, event);
            } else {
                // Update tooltip position
                this.updateTooltipPosition(event);
            }
        } else if (this.hoveredNode) {
            // Reset node and hide tooltip
            this.resetNodeHighlight(this.hoveredNode);
            this.hoveredNode = null;
            this.hideTooltip();
        }
    }
    
    showNodeTooltip(data, event) {
        let content = '';
        
        if (data.type === 'donor') {
            content = `
                <div style="border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 8px; padding-bottom: 5px;">
                    <strong style="color: #64B5F6; font-size: 16px;">Donor Node</strong>
                </div>
                <div><strong>Name:</strong> ${data.name || 'Anonymous'}</div>
                <div><strong>Donation:</strong> RM ${data.amount.toFixed(2)}</div>
                <div><strong>Voucher:</strong> ${data.voucher}</div>
                <div><strong>Transaction ID:</strong> ${data.tx_id}</div>
                <div style="color: #90CAF9; font-size: 11px; margin-top: 5px;">${data.timestamp}</div>
            `;
        } else {
            content = `
                <div style="border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 8px; padding-bottom: 5px;">
                    <strong style="color: #FFAB91; font-size: 16px;">Recipient Node</strong>
                </div>
                <div><strong>Name:</strong> ${data.name}</div>
                <div><strong>Total Received:</strong> RM ${data.totalReceived.toFixed(2)}</div>
                <div><strong>Disbursements:</strong> ${data.disbursements.length}</div>
                <div style="margin-top: 5px; font-size: 12px;">
                    ${data.disbursements.slice(0, 3).map(d => 
                        `<div>• RM${d.amount.toFixed(2)} on ${d.timestamp.split(' ')[0]}</div>`
                    ).join('')}
                    ${data.disbursements.length > 3 ? `<div>• ...and ${data.disbursements.length - 3} more</div>` : ''}
                </div>
            `;
        }
        
        this.tooltip.innerHTML = content;
        this.tooltip.style.opacity = '1';
        this.updateTooltipPosition(event);
    }
    
    updateTooltipPosition(event) {
        const x = event.clientX + 15;
        const y = event.clientY - 10;
        this.tooltip.style.left = `${x}px`;
        this.tooltip.style.top = `${y}px`;
    }
    
    hideTooltip() {
        this.tooltip.style.opacity = '0';
    }
    
    onWindowResize() {
        const rect = this.container.getBoundingClientRect();
        this.width = rect.width;
        this.height = rect.height;
        
        this.camera.aspect = this.width / this.height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.width, this.height);
    }
    
    updateDebug(message) {
        console.log(`ChainExplorer: ${message}`);
        this.debugContainer.textContent = message;
    }
    
    highlightNodeWithConnections(node) {
        // Highlight the node
        node.scale.set(1.3, 1.3, 1.3);
        if (node.material) {
            node.material.opacity = 1;
        }
        
        // Highlight connected links
        const nodeId = node.userData.id;
        this.linkGroup.children.forEach(link => {
            if (link.userData.source === nodeId || link.userData.target === nodeId) {
                link.material.opacity = 1;
                link.material.linewidth = Math.min(5, 2 + link.userData.amount * 0.01);
                link.material.color.set(node.userData.type === 'donor' ? 0x2196F3 : 0xFF5722);
            }
        });
    }
    
    resetNodeHighlight(node) {
        // Reset node
        node.scale.set(1, 1, 1);
        if (node.material) {
            node.material.opacity = 0.85;
        }
        
        // Reset connected links
        const nodeId = node.userData.id;
        this.linkGroup.children.forEach(link => {
            if (link.userData.source === nodeId || link.userData.target === nodeId) {
                link.material.opacity = 0.8;
                link.material.linewidth = Math.min(3, 1 + link.userData.amount * 0.005);
                link.material.color.set(0x90A4AE);
            }
        });
    }
}
