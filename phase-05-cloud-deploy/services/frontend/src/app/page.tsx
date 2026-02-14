'use client';

import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import {
  CheckCircle2,
  Sparkles,
  Zap,
  Target,
  MessageSquare,
  ArrowRight,
  ListTodo,
  Brain,
  Clock
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function LandingPage() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const { scrollYProgress } = useScroll();
  const y = useSpring(useTransform(scrollYProgress, [0, 1], [0, -50]), {
    stiffness: 100,
    damping: 30,
  });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const floatingCards = [
    { text: 'Buy groceries', color: 'from-blue-500 to-cyan-500', delay: 0 },
    { text: 'Team meeting', color: 'from-purple-500 to-pink-500', delay: 0.2 },
    { text: 'Finish report', color: 'from-indigo-500 to-blue-500', delay: 0.4 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-purple-950 text-white overflow-hidden">
      {/* Animated background grid */}
      <div className="fixed inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(to right, rgba(99, 102, 241, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(99, 102, 241, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '4rem 4rem',
        }} />
      </div>

      {/* Gradient orbs */}
      <motion.div
        className="fixed w-96 h-96 rounded-full bg-gradient-to-r from-blue-500/30 to-purple-500/30 blur-3xl"
        style={{
          left: mousePosition.x - 192,
          top: mousePosition.y - 192,
        }}
        transition={{ type: 'spring', damping: 30 }}
      />
      <div className="fixed top-20 right-20 w-96 h-96 rounded-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 blur-3xl animate-pulse" />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 py-20">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="space-y-8"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 backdrop-blur-sm"
            >
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-blue-300">AI-Powered Task Management</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-6xl lg:text-7xl font-black leading-tight"
              style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
            >
              Organize Your Life,{' '}
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Effortlessly
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="text-xl text-slate-300 leading-relaxed max-w-xl"
            >
              Transform chaos into clarity with intelligent task management.
              Let AI handle the complexity while you focus on what matters.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="flex flex-wrap gap-4"
            >
              <Link href="/tasks">
                <motion.button
                  whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(59, 130, 246, 0.4)' }}
                  whileTap={{ scale: 0.95 }}
                  className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl font-bold text-lg shadow-2xl shadow-blue-500/50 flex items-center gap-3 transition-all"
                >
                  Get Started
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </motion.button>
              </Link>

              <Link href="/chat">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl font-bold text-lg hover:bg-white/20 transition-all flex items-center gap-3"
                >
                  <MessageSquare className="w-5 h-5" />
                  Try AI Assistant
                </motion.button>
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="flex items-center gap-6 pt-4"
            >
              <div className="flex -space-x-3">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 border-2 border-slate-950"
                  />
                ))}
              </div>
              <div className="text-sm text-slate-400">
                <span className="font-bold text-white">10,000+</span> tasks completed today
              </div>
            </motion.div>
          </motion.div>

          {/* Right: Floating Cards */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="relative h-[600px] hidden lg:block"
          >
            {floatingCards.map((card, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={{
                  opacity: 1,
                  y: 0,
                  x: Math.sin(index * 2) * 20,
                }}
                transition={{
                  delay: card.delay,
                  duration: 0.8,
                  y: {
                    repeat: Infinity,
                    repeatType: 'reverse',
                    duration: 3 + index,
                    ease: 'easeInOut',
                  },
                }}
                className="absolute"
                style={{
                  top: `${index * 150 + 50}px`,
                  left: `${index * 80}px`,
                }}
              >
                <div className={`bg-gradient-to-br ${card.color} p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-white/20 min-w-[280px]`}>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-lg bg-white/20 flex items-center justify-center mt-1">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-lg mb-2">{card.text}</h3>
                      <div className="flex items-center gap-2 text-sm text-white/80">
                        <Clock className="w-4 h-4" />
                        <span>Due today</span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-5xl font-black mb-6">
              Everything You Need to{' '}
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Stay Organized
              </span>
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Powerful features designed to make task management intuitive and delightful
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: ListTodo,
                title: 'Smart Task Management',
                description: 'Create, organize, and track tasks with an intuitive interface',
                color: 'from-blue-500 to-cyan-500',
                delay: 0,
              },
              {
                icon: Brain,
                title: 'AI Chatbot Assistant',
                description: 'Manage tasks naturally with conversational AI',
                color: 'from-purple-500 to-pink-500',
                delay: 0.1,
              },
              {
                icon: Target,
                title: 'Priority System',
                description: 'Focus on what matters with 5-level priority ranking',
                color: 'from-indigo-500 to-purple-500',
                delay: 0.2,
              },
              {
                icon: Zap,
                title: 'Real-time Sync',
                description: 'Your tasks, everywhere, always up to date',
                color: 'from-pink-500 to-rose-500',
                delay: 0.3,
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: feature.delay, duration: 0.6 }}
                whileHover={{ y: -10, scale: 1.02 }}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-3xl blur-xl group-hover:blur-2xl transition-all" />
                <div className="relative bg-slate-900/50 backdrop-blur-sm border border-white/10 rounded-3xl p-8 h-full hover:border-white/20 transition-all">
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                    <feature.icon className="w-7 h-7" />
                  </div>
                  <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-slate-400 leading-relaxed">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-5xl font-black mb-6">
              Get Started in{' '}
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Three Simple Steps
              </span>
            </h2>
          </motion.div>

          <div className="space-y-12">
            {[
              {
                number: '01',
                title: 'Create Your Account',
                description: 'Sign up in seconds and start organizing your tasks immediately',
                icon: Sparkles,
              },
              {
                number: '02',
                title: 'Add Your Tasks',
                description: 'Use the intuitive interface or chat with our AI assistant',
                icon: MessageSquare,
              },
              {
                number: '03',
                title: 'Stay Productive',
                description: 'Track progress, set priorities, and accomplish your goals',
                icon: Target,
              },
            ].map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2, duration: 0.6 }}
                className="flex gap-8 items-start group"
              >
                <div className="relative">
                  <div className="text-8xl font-black text-transparent bg-gradient-to-br from-blue-500/20 to-purple-500/20 bg-clip-text">
                    {step.number}
                  </div>
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <step.icon className="w-10 h-10" />
                  </div>
                </div>
                <div className="flex-1 pt-8">
                  <h3 className="text-3xl font-bold mb-3">{step.title}</h3>
                  <p className="text-xl text-slate-400">{step.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-3xl blur-3xl" />
            <div className="relative bg-gradient-to-br from-slate-900/80 to-slate-800/80 backdrop-blur-xl border border-white/20 rounded-3xl p-16">
              <h2 className="text-5xl font-black mb-6">
                Ready to Transform Your Productivity?
              </h2>
              <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
                Join thousands of users who have already discovered the power of intelligent task management
              </p>
              <div className="flex flex-wrap gap-4 justify-center">
                <Link href="/tasks">
                  <motion.button
                    whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(59, 130, 246, 0.4)' }}
                    whileTap={{ scale: 0.95 }}
                    className="group px-10 py-5 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl font-bold text-xl shadow-2xl shadow-blue-500/50 flex items-center gap-3"
                  >
                    <ListTodo className="w-6 h-6" />
                    Start Managing Tasks
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </motion.button>
                </Link>

                <Link href="/chat">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-10 py-5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl font-bold text-xl hover:bg-white/20 transition-all flex items-center gap-3"
                  >
                    <MessageSquare className="w-6 h-6" />
                    Chat with AI
                  </motion.button>
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-12 px-6 border-t border-white/10">
        <div className="max-w-7xl mx-auto text-center text-slate-400">
          <p className="text-sm">
            Made with ❤️ using Spec-Driven Development | © 2026 Task Manager
          </p>
        </div>
      </footer>
    </div>
  );
}
