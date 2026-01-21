import { useState } from "react";

import Navbar from "./components/navbar/Navbar";
import Background from "./components/background/Background";
import Signup from "./components/Signup/Signup";
import Signin from "./components/Signin/Signin";

const App = () => {
  const [page, setPage] = useState("home");

  return (
    <div>
      <Navbar setPage={setPage} />

      {page === "home" && <Background />}
      {page === "signup" && <Signup setPage={setPage} />}
      {page === "signin" && <Signin setPage={setPage} />}
    </div>
  );
};

export default App;
