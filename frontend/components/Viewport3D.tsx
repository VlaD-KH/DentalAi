"use client";

import React, { useEffect, useRef } from "react";
import * as THREE from "three";

export const Viewport3D: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#090d16");

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, -28, 20);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    mountRef.current.appendChild(renderer.domElement);

    // Свет
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x00f0ff, 1.4);
    dirLight1.position.set(20, 30, 40);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xff0055, 0.6);
    dirLight2.position.set(-20, -20, 10);
    scene.add(dirLight2);

    // 1. Анатомическая Коронка Зуба #46 с подсвеченной линией уступа (Margin Line)
    const crownGeo = new THREE.CylinderGeometry(5.2, 4.2, 8, 32);
    const crownMat = new THREE.MeshStandardMaterial({
      color: 0xf8fafc,
      roughness: 0.15,
      metalness: 0.1,
    });
    const crownMesh = new THREE.Mesh(crownGeo, crownMat);
    crownMesh.rotation.x = Math.PI / 2.2;
    scene.add(crownMesh);

    // 2. Неоновая светящаяся линия уступа (Margin Line #00F0FF)
    const marginRingGeo = new THREE.TorusGeometry(4.3, 0.2, 16, 100);
    const marginRingMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: false,
    });
    const marginRing = new THREE.Mesh(marginRingGeo, marginRingMat);
    marginRing.position.set(0, -3.8, 0.5);
    marginRing.rotation.x = Math.PI / 2;
    crownMesh.add(marginRing);

    // Анимационный цикл вращения
    let animationFrameId: number;
    const animate = () => {
      crownMesh.rotation.z += 0.004;
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
  }, []);

  return (
    <div className="relative w-full h-full glass-panel-glow rounded-xl overflow-hidden border border-cyan-500/30 flex flex-col">
      {/* Шапка 3D Вьюера */}
      <div className="flex items-center justify-between p-3 bg-slate-950/80 border-b border-slate-800 z-10">
        <div className="flex items-center gap-2">
          <span className="font-bold text-xs text-slate-200 tracking-wide font-mono">3D VIEW HettiRent</span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
            #46 Tooth Prep
          </span>
        </div>

        {/* Occlusal Thickness Heatmap Bar */}
        <div className="flex items-center gap-2 text-[10px] font-mono">
          <span className="text-slate-400">Occlusal Thickness heat-map</span>
          <div className="w-24 h-2.5 rounded heatmap-gradient border border-slate-700 shadow-inner" />
          <div className="flex gap-1 text-[9px]">
            <span className="text-[#00E676]">#00E676</span>
            <span className="text-[#FFD600]">#FFD600</span>
            <span className="text-[#FF1744]">#FF1744</span>
          </div>
        </div>
      </div>

      {/* 3D Canvas */}
      <div ref={mountRef} className="w-full flex-1 relative">
        {/* Метки линии уступа на 3D сцене */}
        <div className="absolute top-12 left-10 text-[11px] font-mono text-cyan-400 flex items-center gap-2 bg-slate-950/80 px-2 py-1 rounded border border-cyan-500/40">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          Margin Line (detect accuracy 99%)
        </div>

        <div className="absolute bottom-16 right-10 text-[11px] font-mono text-emerald-400 bg-slate-950/80 px-2 py-1 rounded border border-emerald-500/40">
          Thickness: 0.72mm [OK &ge; 0.6mm]
        </div>

        {/* 98.5mm Circular Zirconia Nesting Matrix */}
        <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-[90%] bg-slate-950/90 border border-slate-800 rounded-lg p-2 flex items-center justify-between text-xs font-mono backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full border-2 border-cyan-400 flex items-center justify-center text-[10px] text-cyan-400 font-bold">
              98.5
            </div>
            <div className="flex flex-col">
              <span className="text-slate-200 text-[11px] font-sans font-bold">Virtual 98.5mm circular zirconia nesting matrix</span>
              <span className="text-[10px] text-slate-400">Upcera 3D Pro Multi A2, 18mm</span>
            </div>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span>Position: <strong className="text-cyan-400">Slot 4</strong></span>
            <span>Свободно: <strong className="text-emerald-400">42%</strong></span>
            <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
              G-code Ready
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
