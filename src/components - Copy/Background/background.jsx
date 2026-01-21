import "./background.css";
import Home from "../../Assets/home4.jpg";

const Background = () => {
  return (
    <div
      className="background"
      style={{ backgroundImage: `url(${Home})` }}
    >
      <div className="left"></div>

      <div className="right">
        <h1>Welcome to Type-id</h1>
      </div>
    </div>
  );
};

export default Background;
