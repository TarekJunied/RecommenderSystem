import ChooseLayout from "../layout/ChooseLayout";
import { AlgorithmPortfolio, measures } from "../constants";
import StartButton from "../components/StartButton"
import RedirectButton from "../components/RedirectButton";
import { useNavigate } from 'react-router-dom';
import AlgorithmScore from "../components/AlgorithmScore";
import { Tooltip } from 'react-tooltip'
const translateMeasureIntoPythonSyntax = (jsMeasure) => {
    // Make the string lowercase
    const lowercaseMeasure = jsMeasure.toLowerCase();

    // Replace spaces with underscores
    const pythonSyntaxMeasure = lowercaseMeasure.replace(/ /g, '_');

    return pythonSyntaxMeasure;
};



const RecommendPage = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const recommendationParam = urlParams.get('recommendation');
    const algoMeasureDictParam = urlParams.get('algoMeasureDict')
    const relevantMeasuresParam = urlParams.get('relevantMeasures')
    const sessionTokenParam = urlParams.get('sessionToken');

    const recommendationData = JSON.parse(decodeURIComponent(recommendationParam));
    const algoMeasureDict = JSON.parse(decodeURIComponent(algoMeasureDictParam));
    const sessionToken = decodeURIComponent(sessionTokenParam)
    const relevantMeasures = JSON.parse(decodeURIComponent(relevantMeasuresParam));



    const getPredictedMeasureValue = (DiscoveryAlgorithm, measure) => {
        let key = DiscoveryAlgorithm + "-" + translateMeasureIntoPythonSyntax(measure)
        return algoMeasureDict[key]
    }


    const navigate = useNavigate();


    const handleMineButtonClick = () => {
        navigate(`/mine?sessionToken=${sessionToken}`);
    };
    const handlePredictionButtonClick = () => {
        navigate(`/explain?sessionToken=${sessionToken}&relevantMeasures=${encodeURIComponent(JSON.stringify(relevantMeasures))}`)
    }


    const handleMainMenuButtonClick = () => {
        navigate("/start")
    };

    AlgorithmPortfolio.sort((a, b) => {
        // Assuming recommendationData[DiscoveryAlgorithm] holds a sortable value.
        // Adjust the comparison for the specific data type and desired order.
        return recommendationData[b] - recommendationData[a]; // For descending order
        // Use recommendationData[a] - recommendationData[b] for ascending order
    });

    const headingStyle = {

        alignSelf: "center",
        color: "white",
        fontSize: "5vw"

    }

    const toolTipStyle = {
        fontSize: "2vw"
    }
    const tooltipTexts = {};

    AlgorithmPortfolio.forEach(DiscoveryAlgorithm => {
        tooltipTexts[DiscoveryAlgorithm] = `Predicted Values:<br/>${relevantMeasures.map(measure => `${measure}:${getPredictedMeasureValue(DiscoveryAlgorithm, measure)}<br/>`).join('')}`
    });
    const buttonStyle = {
        display: 'flex',        // Equivalent to 'flex'
        width: '100%',          // Equivalent to 'w-full'
        justifyContent: 'center',
        marginBottom: "5vh"
    };

    function translateAlgoName(algorithmName) {
        let ret;
        switch (algorithmName) {

            case "inductive":
                ret = "IM"
                break;
            case "inductive_direct":
                ret = "IMd"
                break;
            case "inductive_infrequent":
                ret = "IMf"
                break;
            case "alpha_plus":
                ret = "ALPHA +"
                break;
            default:
                ret = algorithmName.toUpperCase()
        }
        return ret;
    }

    return (
        <ChooseLayout>
            <h1 style={headingStyle}>Leaderboard  🏆</h1>


            <div className="flex justify-center w-screen mt-10">
                <div className="flex-row">
                    {AlgorithmPortfolio.map((DiscoveryAlgorithm, index) => (
                        <div key={index} style={{
                            marginTop: index === 0 ? "0" : "5vh",
                            width: "55vw" // add top margin for all but the first item
                        }}>
                            <a
                                data-tooltip-id={`${DiscoveryAlgorithm}sToolTip`}
                                data-tooltip-html={tooltipTexts[DiscoveryAlgorithm]}
                                data-tooltip-place="top"

                            >
                                <AlgorithmScore
                                    placement={index + 1}
                                    algorithmName={translateAlgoName(DiscoveryAlgorithm)}
                                    algorithmScore={recommendationData[DiscoveryAlgorithm]}


                                />
                            </a>

                            <Tooltip id={`${DiscoveryAlgorithm}sToolTip`}
                                style={toolTipStyle}
                                place="top" />
                        </div>
                    ))}

                </div>
            </div>
            <div className="flex flex-col items-center space-y-10">
                <div className="flex-grow"></div>
                <div style={buttonStyle}>

                    <RedirectButton
                        text="Explain the predictions"
                        onClick={handlePredictionButtonClick}
                    />
                </div>
                <div style={buttonStyle}>
                    <RedirectButton
                        text="Mine a process model"
                        onClick={handleMineButtonClick}
                    />
                </div>
                <div style={buttonStyle}>
                    <RedirectButton
                        text="Back to start"
                        onClick={handleMainMenuButtonClick}
                    />
                </div>



            </div>

        </ChooseLayout >
    );
};

export default RecommendPage;
