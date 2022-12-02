import {
    Button,
    Form,
    FormControl,
    FormGroup
} from "react-bootstrap";

import React, { useState } from 'react';
import { useRecoilState, useSetRecoilState } from "recoil";
import { Body_login_auth_token_post, OpenAPI, SamplesService, UsersService } from "../generated/api";
import { LoggedUser } from "../common/User";
import User from "../common/User";
import { NavigateFunction, redirect, useNavigate } from "react-router-dom";
import useSetError from '../common/Error';


interface LoginState {
    username: string,
    password: string,
    inProgress: boolean,
}


export const Login = () => {
    const setUser = useSetRecoilState(LoggedUser);
    const [state, setState] = useState<LoginState>({ username: "testuser", password: "pass", inProgress: false });
    const navigate = useNavigate();
    const setError = useSetError();

    return <div>
        <Form onSubmit={async (e) => {
            e.preventDefault();
            let user;
            try {
                user = await doLogin(state);
            } catch(err) {
                //setError({message: "Login failed"});
                setUser(null);
                return navigate("/login", {
                    state: { error: { message: "Login failed" } },
                    replace: false,
                })
            }
            setUser(user);
            navigate("/samples");
        }}>
            <Form.Group className="mb-3" controlId="formUsername">
                <Form.Label>Username</Form.Label>
                <Form.Control placeholder="Username"
                              value={state.username}
                              onChange={(e) => setState({ ...state, username: e.target.value})} />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formBasicPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password"
                              placeholder="Password"
                              value={state.password}
                              onChange={(e) => setState({...state, password: e.target.value})}/>
            </Form.Group>
            <Button disabled={state.inProgress} variant="primary" type="submit">
                Login
            </Button>
        </Form>
    </div>;
}

async function doLogin(user: LoginState): Promise<User | null> {
      OpenAPI.TOKEN = "";
      let data: Body_login_auth_token_post = {
        username: user.username,
        password: user.password
      }
      OpenAPI.BASE = "http://localhost:8000"
      let r = await UsersService.loginAuthTokenPost(data)
      console.log(r);
      OpenAPI.TOKEN = r.access_token;
    //   let r2 = await SamplesService.getOwnSamplesSamplesGet();
    //   console.log(r2);
      return {name: user.username};
}