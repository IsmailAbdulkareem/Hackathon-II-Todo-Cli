'use client';

import React, { useState } from 'react';
import { Bell, X, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNotifications } from '@/hooks/use-notifications';
import { cn } from '@/lib/utils';

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, isConnected, error, clearNotifications, removeNotification } = useNotifications();

  const unreadCount = notifications.length;

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <div className="relative">
      {/* Bell Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className="relative h-10 w-10 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-800"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
        {!isConnected && (
          <span className="absolute -bottom-1 -right-1 flex h-3 w-3 items-center justify-center rounded-full bg-yellow-500 border-2 border-white dark:border-neutral-900" />
        )}
      </Button>

      {/* Notification Panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Panel */}
          <div className="absolute right-0 top-12 z-50 w-96 max-h-[500px] overflow-hidden rounded-2xl border-2 border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b-2 border-neutral-200 dark:border-neutral-700">
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-lg">Notifications</h3>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 text-xs font-bold bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {/* Connection Status */}
                <div className="flex items-center gap-1.5">
                  <div className={cn(
                    "h-2 w-2 rounded-full",
                    isConnected ? "bg-green-500 animate-pulse" : "bg-yellow-500"
                  )} />
                  <span className="text-xs text-neutral-500 dark:text-neutral-400">
                    {isConnected ? 'Connected' : 'Reconnecting...'}
                  </span>
                </div>
                {unreadCount > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearNotifications}
                    className="text-xs h-7"
                  >
                    Clear all
                  </Button>
                )}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-950 border-b-2 border-red-200 dark:border-red-800">
                <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
                  <AlertCircle className="h-4 w-4" />
                  <p className="text-sm font-medium">{error}</p>
                </div>
              </div>
            )}

            {/* Notifications List */}
            <div className="max-h-[400px] overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-12 text-neutral-500 dark:text-neutral-400">
                  <CheckCircle className="h-12 w-12 mb-3 opacity-20" />
                  <p className="font-medium">No notifications</p>
                  <p className="text-sm">You're all caught up!</p>
                </div>
              ) : (
                <div className="divide-y divide-neutral-200 dark:divide-neutral-700">
                  {notifications.map((notification, index) => (
                    <div
                      key={index}
                      className="group relative p-4 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
                    >
                      <button
                        onClick={() => removeNotification(index)}
                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="h-4 w-4 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200" />
                      </button>

                      <div className="flex items-start gap-3 pr-6">
                        <div className="flex-shrink-0 mt-1">
                          <Bell className="h-5 w-5 text-blue-500" />
                        </div>
                        <div className="flex-1 min-w-0">
                          {notification.data.title && (
                            <h4 className="font-semibold text-sm text-neutral-900 dark:text-neutral-100 mb-1">
                              {notification.data.title}
                            </h4>
                          )}
                          {notification.data.message && (
                            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2">
                              {notification.data.message}
                            </p>
                          )}
                          <p className="text-xs text-neutral-500 dark:text-neutral-500">
                            {formatTimestamp(notification.data.timestamp)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
