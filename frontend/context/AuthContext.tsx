import React, { createContext, ReactNode, useContext, useState } from 'react';

export type User = {
    id: string;
    name: string;
    email: string;
    avatar?: string;
};

type AuthContextType = {
    user: User | null;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    signup: (name: string, email: string, password: string) => Promise<boolean>;
    logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>({
        id: '1',
        name: 'Guest User',
        email: 'guest@example.com',
    });
    const [isLoading, setIsLoading] = useState(false);

    const login = async (email: string, password: string): Promise<boolean> => {
        setIsLoading(true);
        // Simulate API call
        await new Promise((r) => setTimeout(r, 1500));
        setIsLoading(false);
        if (email && password.length >= 6) {
            setUser({
                id: '1',
                name: email.split('@')[0],
                email,
            });
            return true;
        }
        return false;
    };

    const signup = async (name: string, email: string, password: string): Promise<boolean> => {
        setIsLoading(true);
        await new Promise((r) => setTimeout(r, 1500));
        setIsLoading(false);
        if (name && email && password.length >= 6) {
            setUser({ id: '1', name, email });
            return true;
        }
        return false;
    };

    const logout = () => {
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, isLoading, login, signup, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
    return ctx;
}
