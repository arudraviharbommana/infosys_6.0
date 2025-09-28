// src/components/ThreeDScene.jsx
import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

const ThreeDScene = () => {
    const mountRef = useRef(null);
    const sceneRef = useRef(null);
    const rendererRef = useRef(null);
    const frameRef = useRef(null);

    useEffect(() => {
        const currentMount = mountRef.current;
        if (!currentMount) return;

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a1a);
        sceneRef.current = scene;

        // Camera setup
        const camera = new THREE.PerspectiveCamera(
            75,
            currentMount.clientWidth / currentMount.clientHeight,
            0.1,
            1000
        );
        camera.position.z = 8;

        // Renderer setup
        const renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        rendererRef.current = renderer;
        currentMount.appendChild(renderer.domElement);

        // Lighting setup
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        scene.add(directionalLight);

        // Create multiple geometric shapes representing skills/data
        const shapes = [];
        const colors = [0x4fc3f7, 0x81c784, 0xffb74d, 0xe57373, 0xba68c8, 0x64b5f6];

        // Central rotating cube (main skill processor)
        const cubeGeometry = new THREE.BoxGeometry(1.5, 1.5, 1.5);
        const cubeMaterial = new THREE.MeshPhongMaterial({ 
            color: colors[0],
            transparent: true,
            opacity: 0.8
        });
        const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
        cube.position.set(0, 0, 0);
        cube.castShadow = true;
        scene.add(cube);
        shapes.push({ mesh: cube, type: 'cube' });

        // Orbiting spheres (representing skills)
        for (let i = 0; i < 6; i++) {
            const sphereGeometry = new THREE.SphereGeometry(0.3, 16, 16);
            const sphereMaterial = new THREE.MeshPhongMaterial({ 
                color: colors[i % colors.length],
                transparent: true,
                opacity: 0.7
            });
            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            
            const angle = (i / 6) * Math.PI * 2;
            const radius = 3;
            sphere.position.set(
                Math.cos(angle) * radius,
                Math.sin(angle * 0.5) * 1.5,
                Math.sin(angle) * radius
            );
            sphere.castShadow = true;
            scene.add(sphere);
            shapes.push({ 
                mesh: sphere, 
                type: 'sphere', 
                angle: angle,
                radius: radius,
                speed: 0.01 + Math.random() * 0.02
            });
        }

        // Floating geometric particles
        const particleCount = 20;
        const particleGeometry = new THREE.TetrahedronGeometry(0.1);
        for (let i = 0; i < particleCount; i++) {
            const particleMaterial = new THREE.MeshPhongMaterial({ 
                color: colors[Math.floor(Math.random() * colors.length)],
                transparent: true,
                opacity: 0.5
            });
            const particle = new THREE.Mesh(particleGeometry, particleMaterial);
            particle.position.set(
                (Math.random() - 0.5) * 12,
                (Math.random() - 0.5) * 8,
                (Math.random() - 0.5) * 12
            );
            scene.add(particle);
            shapes.push({ 
                mesh: particle, 
                type: 'particle',
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 0.02,
                    (Math.random() - 0.5) * 0.02,
                    (Math.random() - 0.5) * 0.02
                )
            });
        }

        // Animation loop
        const animate = () => {
            frameRef.current = requestAnimationFrame(animate);

            // Animate central cube
            const cube = shapes[0].mesh;
            cube.rotation.x += 0.005;
            cube.rotation.y += 0.01;
            cube.rotation.z += 0.007;

            // Animate orbiting spheres
            shapes.slice(1, 7).forEach((shape, index) => {
                if (shape.type === 'sphere') {
                    shape.angle += shape.speed;
                    const x = Math.cos(shape.angle) * shape.radius;
                    const z = Math.sin(shape.angle) * shape.radius;
                    const y = Math.sin(shape.angle * 0.5) * 1.5;
                    
                    shape.mesh.position.set(x, y, z);
                    shape.mesh.rotation.y += 0.02;
                    shape.mesh.rotation.x += 0.01;
                }
            });

            // Animate floating particles
            shapes.slice(7).forEach(shape => {
                if (shape.type === 'particle') {
                    shape.mesh.position.add(shape.velocity);
                    shape.mesh.rotation.x += 0.02;
                    shape.mesh.rotation.y += 0.03;

                    // Boundary checking - bounce off edges
                    if (Math.abs(shape.mesh.position.x) > 6) {
                        shape.velocity.x *= -1;
                    }
                    if (Math.abs(shape.mesh.position.y) > 4) {
                        shape.velocity.y *= -1;
                    }
                    if (Math.abs(shape.mesh.position.z) > 6) {
                        shape.velocity.z *= -1;
                    }
                }
            });

            // Gentle camera movement
            const time = Date.now() * 0.001;
            camera.position.x = Math.sin(time * 0.2) * 0.5;
            camera.position.y = Math.cos(time * 0.15) * 0.3;
            camera.lookAt(scene.position);

            renderer.render(scene, camera);
        };

        animate();

        // Handle window resize
        const handleResize = () => {
            if (!currentMount) return;
            
            const width = currentMount.clientWidth;
            const height = currentMount.clientHeight;
            
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        };

        window.addEventListener('resize', handleResize);

        // Mouse interaction
        const mouse = new THREE.Vector2();
        const raycaster = new THREE.Raycaster();

        const handleMouseMove = (event) => {
            const rect = currentMount.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(scene.children);

            // Reset all materials
            scene.children.forEach(child => {
                if (child.material && child.material.emissive) {
                    child.material.emissive.setHex(0x000000);
                }
            });

            // Highlight intersected objects
            if (intersects.length > 0) {
                intersects[0].object.material.emissive.setHex(0x444444);
            }
        };

        currentMount.addEventListener('mousemove', handleMouseMove);

        // Cleanup function
        return () => {
            if (frameRef.current) {
                cancelAnimationFrame(frameRef.current);
            }
            
            window.removeEventListener('resize', handleResize);
            
            if (currentMount) {
                currentMount.removeEventListener('mousemove', handleMouseMove);
                if (renderer.domElement && currentMount.contains(renderer.domElement)) {
                    currentMount.removeChild(renderer.domElement);
                }
            }

            // Dispose of geometries and materials
            shapes.forEach(shape => {
                if (shape.mesh.geometry) {
                    shape.mesh.geometry.dispose();
                }
                if (shape.mesh.material) {
                    shape.mesh.material.dispose();
                }
            });

            if (renderer) {
                renderer.dispose();
            }
        };
    }, []);

    return (
        <div 
            ref={mountRef} 
            className="three-d-scene" 
            style={{ 
                width: '100%', 
                height: '300px',
                borderRadius: '8px',
                overflow: 'hidden',
                background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)'
            }} 
        />
    );
};

export default ThreeDScene;