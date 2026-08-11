"use client";

import React, { useEffect, useRef } from "react";
import * as THREE from "three";

interface Viewport3DProps {
  scanUrl?: string;
  crownUrl?: string;
}

export const Viewport3D: React.FC<Viewport3DProps> = ({ scanUrl, crownUrl }) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;

    // 1. Сцена, Камера и Рендерер
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#0f172a"); // Dark slate slate-900 background

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, -40, 30);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    mountRef.current.appendChild(renderer.domElement);

    // 2. Освещение (Сценический стоматологический свет)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight1.position.set(20, 20, 40);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.8);
    dirLight2.position.set(-20, -20, -10);
    scene.add(dirLight2);

    // 3. Синтетическая 3D сетка короны (демо-модель для 3D Viewport)
    const crownGeometry = new THREE.ConeGeometry(5, 8, 32);
    const crownMaterial = new THREE.MeshStandardMaterial({
      color: 0xf8fafc,
      roughness: 0.2,
      metalness: 0.1,
    });
    const crownMesh = new THREE.Mesh(crownGeometry, crownMaterial);
    crownMesh.rotation.x = Math.PI / 2;
    scene.add(crownMesh);

    // Сетка челюсти
    const archGeometry = new THREE.TorusGeometry(12, 3, 16, 100, Math.PI);
    const archMaterial = new THREE.MeshStandardMaterial({
      color: 0xf1f5f9,
      roughness: 0.4,
      wireframe: true,
    });
    const archMesh = new THREE.Mesh(archGeometry, archMaterial);
    archMesh.position.set(0, -2, -2);
    scene.add(archMesh);

    // 4. Анимационный цикл вращения 3D сцены
    let animationFrameId: number;
    const animate = () => {
      crownMesh.rotation.z += 0.005;
      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, [scanUrl, crownUrl]);

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden border border-slate-700 bg-slate-900 shadow-2xl">
      <div className="absolute top-4 left-4 z-10 bg-slate-800/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-mono text-cyan-400">
        Three.js 3D Viewport — Zirconia Upcera A2 (#FDI-46)
      </div>
      <div ref={mountRef} className="w-full h-full" />
    </div>
  );
};
