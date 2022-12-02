import { atom, useRecoilState } from "recoil";

interface User {
    name: string
}

export default User;

export const LoggedUser = atom<User | null>({key: "LoggedUser", default: null});