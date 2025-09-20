import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Color } from 'three';

const WavySphere = () => {
  const meshRef = useRef();
  
  // Use useFrame to create an animation loop
  useFrame(({ clock }) => {
    if (meshRef.current) {
      // Animate the sphere's scale
      const scale = 1 + Math.sin(clock.elapsedTime) * 0.1;
      meshRef.current.scale.set(scale, scale, scale);
      
      // Rotate the sphere
      meshRef.current.rotation.y += 0.005;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshPhysicalMaterial
        color={new Color('#00aaff')}
        roughness={0.2}
        metalness={0.8}
        clearcoat={0.5}
        clearcoatRoughness={0.2}
        transparent
        opacity={0.8}
      />
    </mesh>
  );
};

const ThreeDScene = () => {
  return (
    <Canvas
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        zIndex: -1,
        width: '100%',
        height: '100vh',
      }}
      camera={{ position: [0, 0, 5] }}
    >
      {/* Lights */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} color="#ffffff" />
      <pointLight position={[-10, -10, -10]} intensity={1} color="#ff00aa" />

      {/* The animated sphere */}
      <WavySphere />
    </Canvas>
  );
};

export default ThreeDScene;