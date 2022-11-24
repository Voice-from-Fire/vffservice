import React, { useContext } from 'react';
import logo from './logo.svg';
import './App.css';
import User from './common/User';
import { Button, Container, Nav, Navbar, Stack } from 'react-bootstrap';
import { Link, Routes, Route, Outlet } from 'react-router-dom';

import { Login } from './components/Login';
import { SampleList } from './components/Samples';
import { About } from './components/About';
import { AppCtx } from './common/AppContext';

const Layout = () => {
  const appContext = useContext(AppCtx);
  return <div className="App">
    <Navbar bg="dark" variant="dark">
      <Container>
        <Navbar.Brand href="#home">VoiceFromFire</Navbar.Brand>
        <Nav className="me-auto">
          <Nav.Link as={Link} to="about">About</Nav.Link>

          {
            <>
              <Nav.Link as={Link} to="login">Login</Nav.Link>
            </>
          }
          {
            <>
              <Nav.Link as={Link} to="samples">My samples</Nav.Link>
              <Nav.Link as={Link} to="labels">Label others</Nav.Link>
              <Nav.Link as={Link} to="labels">Logout</Nav.Link>
            </>
          }
        </Nav>
      </Container>
    </Navbar>
    <Outlet />
  </div>
}

function App() {

  return <Routes>
    <Route path="/" element={<Layout />}>
      <Route index element={<About />} />
      <Route path="about" element={<About />} />
      <Route path="samples" element={<SampleList />} />
      <Route path="*" element={<About />} />
    </Route>
  </Routes>;
  // return (
  //   <div className="App">
  //     <Navbar bg="dark" variant="dark">
  //       <Container>
  //         <Navbar.Brand href="#home">VoiceFromFire</Navbar.Brand>
  //         <Nav className="me-auto">
  //           <Nav.Link href="#about">About</Nav.Link>
  //           <Nav.Link href="#samples">My samples</Nav.Link>
  //           <Nav.Link href="#labels">Label others</Nav.Link>
  //         </Nav>
  //       </Container>
  //     </Navbar>
  //     <br />
  //     <div className="container">

  //       <Route path="/login" component={() => <Login />} />
  //       <Route path="/about" component={() => <About />} />
  //       <Route path="/login" component={() => <Samples />} />

  //       {/* <ProtectedRoute path="/search" component={Search} />
  //         <ProtectedRoute path="/labels" component={Labels} />
  //         <ProtectedRoute path="/entry/:id" component={Entry} />
  //         <ProtectedRoute path="/item/:id" component={Item} />
  //         <ProtectedRoute path="/stats/:id" component={Stats} />
  //         <ProtectedRoute path="/entries" component={Entries} />
  //         <ProtectedRoute path="/narrators" component={Narrators} />
  //         <ProtectedRoute path="/narrator/:id" component={Narrator} />
  //         <ProtectedRoute path="/export" component={Export} />
  //         <ProtectedRoute exact path="/" component={Home} />
  //       </Switch>} */}
  //     </div>
  //   </div>
  // );
}

export default App;
