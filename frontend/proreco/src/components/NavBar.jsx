import { Component } from "react";
import { Link } from "react-router-dom";
import reactLogo from '../assets/react.svg';
import Button from "./Button.jsx";
import styles from "../styles.js";
import "./styles/NavBarStyles.css";

class NavBar extends Component {
    state = { clicked: false };

    handleClick = () => {
        this.setState({ clicked: !this.state.clicked });
    }

    render() {
        return (
            <div className="navbar">
                <nav>
                    <Link to="/home">
                        <img src={reactLogo} alt="React Logo" />
                    </Link>
                    <div>
                        <ul id="navbar" className={this.state.clicked ? "navbar active" : "navbar"}>
                            <li><Link to="/home" className="active">Home</Link></li>
                            <li><Link to="/about">About</Link></li>
                            <li><Link to="/process-mining">Process Mining</Link></li>
                            <li><Link to="/contact">Contact</Link></li>
                            <li><Link to="/source">Source</Link></li>
                            <li>
                                <div className={`justify-between ${styles.flexCenter}`}>
                                    <Button text="Get started" styles="bg-orange-gradient" />
                                </div>
                            </li>
                        </ul>
                    </div>
                    <div id="mobile" onClick={this.handleClick}>
                        <i id="bar" className={this.state.clicked ? "fas fa-times" : "fas fa-bars"}></i>
                    </div>
                </nav>
            </div>
        );
    }
}

export default NavBar;
