import { createContext } from 'react';
import User from './User';


interface AppContext {
    user: User
}

export default AppContext;


export const AppCtx = createContext<AppContext | null>(null);