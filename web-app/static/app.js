// app.js

// Function to analyze the input sentence
function analyzeSentence() {
    const sentence = document.getElementById('sentenceInput').value;
    const uploadMessage = document.getElementById('uploadMessage');
    uploadMessage.classList.remove('hidden'); // Show upload message

    fetch('/checkSentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sentence })
    })
    .then(response => response.json())
    .then(data => {
        const requestId = data.request_id;
        // Keep checking until the analysis is available
        fetchAnalysisWithRetry(requestId, 10);  // Max retries: 10
    })
    .catch(error => console.error('Error:', error));
}

let isRecording = false;
let recognition;

function startDictation() {
  const speakButton = document.getElementById("speakButton");

  if (!('webkitSpeechRecognition' in window)) {
    alert("Your browser does not support speech recognition. Please try Chrome.");
    return;
  }

  if (!recognition) {
    // Initialize speech recognition
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = function () {
      console.log("Voice recognition started.");
    };

    recognition.onresult = function (event) {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript + " ";
        }
      }
      document.getElementById("sentenceInput").value += transcript;
    };

    recognition.onerror = function (event) {
      console.error("Recognition error:", event.error);
    };

    recognition.onend = function () {
      console.log("Voice recognition ended.");
      stopRecognition(speakButton);  // Reset button when recognition ends
    };
  }

  if (!isRecording) {
    startRecognition(speakButton);
  } else {
    stopRecognition(speakButton);
  }
}

function startRecognition(button) {
  recognition.start();
  isRecording = true;
  button.innerText = "Recording..."; // Update button text to "Recording..."
}

function stopRecognition(button) {
  recognition.stop();
  isRecording = false;
  button.innerText = "🎤 Speak"; // Update button text back to "🎤 Speak"
}

// Function to fetch analysis with retries
function fetchAnalysisWithRetry(requestId, retries) {
    if (retries <= 0) {
        console.error("Failed to retrieve analysis after multiple attempts");
        return;
    }

    setTimeout(() => {
        fetch(`/get_analysis?request_id=${requestId}`)
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    console.error(data.message);
                    // Retry if no analysis found yet
                    fetchAnalysisWithRetry(requestId, retries - 1);
                } else {
                    // Pass the data to visualization functions
                    visualizeResults(data);
                    // Call visualizeEmotionIntensity
                    visualizeEmotionIntensity(requestId);
                    document.getElementById('uploadMessage').classList.add('hidden'); // Hide upload message once results are available
                }
            })
            .catch(error => {
                console.error('Error:', error);
                fetchAnalysisWithRetry(requestId, retries - 1);
            });
    }, 5000);  // Retry interval set to 5 seconds
}

// Function to visualize all results
function visualizeResults(data) {
    displaySummary(data);
    visualizeTopics(data);
    visualizeOverallEmotions(data);
    visualizeSentimentTrend(data);
    visualizeSentimentIntensity(data);
    visualizeSentimentDistribution(data);
    visualizeEmotionalShifts(data);
    visualizeEntities(data); 
}

// Function to display the summary text
function displaySummary(data) {
    document.getElementById('summaryText').textContent = data.summary;
}

// Function to visualize topics using a word cloud
function visualizeTopics(data) {
    const topics = data.topics;
    // Flatten the topics into words and weights
    let words = [];
    topics.forEach(topic => {
        // topic[1] is the topic string
        const wordWeights = topic[1].split('+').map(item => {
            const parts = item.trim().split('*');
            return {
                text: parts[1].replace(/"/g, ''),
                size: parseFloat(parts[0]) * 1000  // Scale the size appropriately
            };
        });
        words = words.concat(wordWeights);
    });

    // Set dimensions
    const width = 500;
    const height = 300;

    // Remove any existing SVG
    d3.select("#topics").selectAll("*").remove();

    const svg = d3.select("#topics").append("svg")
        .attr("width", width)
        .attr("height", height);

    const layout = d3.layout.cloud()
        .size([width, height])
        .words(words)
        .padding(5)
        .rotate(() => ~~(Math.random() * 2) * 90)
        .fontSize(d => d.size)
        .on("end", draw);

    layout.start();

    function draw(words) {
        svg.append("g")
            .attr("transform", `translate(${width / 2}, ${height / 2})`)
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", d => `${d.size}px`)
            .style("fill", () => `hsl(${Math.random() * 360},100%,50%)`)
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${[d.x, d.y]})rotate(${d.rotate})`)
            .text(d => d.text);
    }
}

// Function to visualize overall emotions using a pie chart
function visualizeOverallEmotions(data) {
    const emotions = data.overall_emotions;
    const emotionCounts = {};
    emotions.forEach(emotion => {
        emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
    });

    const pieData = Object.entries(emotionCounts).map(([emotion, count]) => ({ emotion, count }));

    // Set dimensions
    const width = 300;
    const height = 300;
    const radius = Math.min(width, height) / 2;

    // Remove existing SVG
    d3.select("#overallEmotions").selectAll("*").remove();

    const svg = d3.select("#overallEmotions").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const color = d3.scaleOrdinal()
        .domain(pieData.map(d => d.emotion))
        .range(d3.schemeCategory10);

    const pie = d3.pie()
        .value(d => d.count);

    const data_ready = pie(pieData);

    svg.selectAll('whatever')
        .data(data_ready)
        .join('path')
        .attr('d', d3.arc()
            .innerRadius(0)
            .outerRadius(radius)
        )
        .attr('fill', d => color(d.data.emotion))
        .attr("stroke", "#fff")
        .style("stroke-width", "2px")
        .style("opacity", 0.7);

    // Add labels
    svg.selectAll('mySlices')
        .data(data_ready)
        .enter()
        .append('text')
        .text(d => `${d.data.emotion} (${d.data.count})`)
        .attr("transform", d => `translate(${d3.arc().innerRadius(0).outerRadius(radius).centroid(d)})`)
        .style("text-anchor", "middle")
        .style("font-size", 12);

    // Add legend
    const legend = svg.append("g")
        .attr("transform", `translate(${width / 2 + 20}, ${-height / 2})`);

    legend.selectAll(".legend-item")
        .data(pieData)
        .enter()
        .append("g")
        .attr("class", "legend-item")
        .attr("transform", (d, i) => `translate(0, ${i * 20})`)
        .call(g => {
            g.append("rect")
                .attr("width", 10)
                .attr("height", 10)
                .attr("fill", d => color(d.emotion));

            g.append("text")
                .attr("x", 15)
                .attr("y", 10)
                .text(d => d.emotion)
                .style("font-size", 12);
        });
}

// Function to visualize sentiment trend using a line chart
function visualizeSentimentTrend(data) {
    const sentimentTrend = data.sentiment_trend;

    // Remove previous visualization
    d3.select("#sentimentTrend").selectAll("*").remove();

    // Set dimensions and margins
    const width = 600;
    const height = 300;
    const margin = { top: 20, right: 100, bottom: 50, left: 50 };

    const svg = d3.select("#sentimentTrend")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create scales
    const x = d3.scaleLinear()
        .domain(d3.extent(sentimentTrend, d => d.sentence_index))
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([-1, 1])
        .range([height, 0]);

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(10));

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add line path
    svg.append("path")
        .datum(sentimentTrend)
        .attr("fill", "none")
        .attr("stroke", "#4CAF50")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(d => x(d.sentence_index))
            .y(d => y(d.compound))
        );

    // Add points
    svg.selectAll("dot")
        .data(sentimentTrend)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.sentence_index))
        .attr("cy", d => y(d.compound))
        .attr("r", 3)
        .attr("fill", "#4CAF50");

    // Add legend
    const legend = svg.append("g")
        .attr("transform", `translate(${width + 20}, ${0})`)
        .call(g => {
            g.append("rect")
                .attr("width", 10)
                .attr("height", 10)
                .attr("fill", "#4CAF50");

            g.append("text")
                .attr("x", 15)
                .attr("y", 10)
                .text("Sentiment Trend")
                .style("font-size", 12);
        });
}

// Function to visualize sentiment intensity per sentence using a bar chart
function visualizeSentimentIntensity(data) {
    const sentences = data.sentences;
    const sentenceIndices = sentences.map((_, i) => i);
    const compoundScores = sentences.map(sentence => sentence.analysis.compound);

    // Set dimensions
    const width = 600;
    const height = 300;
    const margin = { top: 20, right: 30, bottom: 50, left: 50 };

    // Remove existing SVG
    d3.select("#sentimentIntensity").selectAll("*").remove();

    const svg = d3.select("#sentimentIntensity")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create scales
    const x = d3.scaleBand()
        .domain(sentenceIndices)
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([-1, 1])
        .range([height, 0]);

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).tickValues(x.domain().filter((d, i) => !(i % 5))));

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add bars
    svg.selectAll(".bar")
        .data(compoundScores)
        .enter()
        .append("rect")
        .attr("x", (d, i) => x(i))
        .attr("width", x.bandwidth())
        .attr("y", d => y(Math.max(0, d)))
        .attr("height", d => Math.abs(y(d) - y(0)))
        .attr("fill", d => d >= 0 ? "#4caf50" : "#f44336");
}

// Function to visualize sentiment distribution using a histogram
function visualizeSentimentDistribution(data) {
    const compoundScores = data.sentences.map(sentence => sentence.analysis.compound);

    // Set dimensions
    const width = 600;
    const height = 300;
    const margin = { top: 20, right: 30, bottom: 50, left: 50 };

    // Remove existing SVG
    d3.select("#sentimentDistribution").selectAll("*").remove();

    const svg = d3.select("#sentimentDistribution")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create x-axis scale
    const x = d3.scaleLinear()
        .domain([-1, 1])  // Sentiment scores range
        .range([0, width]);

    // Generate histogram data
    const histogram = d3.histogram()
        .domain(x.domain())
        .thresholds(x.ticks(20));

    const bins = histogram(compoundScores);

    // Create y-axis scale
    const y = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)])
        .range([height, 0]);

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add bars
    svg.selectAll("rect")
        .data(bins)
        .enter()
        .append("rect")
        .attr("x", 1)
        .attr("transform", d => `translate(${x(d.x0)}, ${y(d.length)})`)
        .attr("width", d => x(d.x1) - x(d.x0) - 1)
        .attr("height", d => height - y(d.length))
        .style("fill", "#69b3a2");
}

// Function to visualize emotional shifts using a stacked area chart
function visualizeEmotionalShifts(data) {
    const sentences = data.sentences;
    const emotionTypes = ["Happy", "Angry", "Surprise", "Sad", "Fear", "Neutural"];
    const emotionData = [];

    sentences.forEach((sentence, index) => {
        const emotions = sentence.emotions;
        const emotionCounts = {};
        emotionTypes.forEach(emotion => {
            emotionCounts[emotion] = emotions.includes(emotion) ? 1 : 0;
        });
        emotionData.push({ sentence_index: index, ...emotionCounts });
    });

    // Prepare data for stack
    const stack = d3.stack().keys(emotionTypes);
    const stackedData = stack(emotionData);

    // Set dimensions
    const width = 600;
    const height = 300;
    const margin = { top: 20, right: 30, bottom: 50, left: 50 };

    // Remove existing SVG
    d3.select("#emotionalShifts").selectAll("*").remove();

    const svg = d3.select("#emotionalShifts")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create scales
    const x = d3.scaleLinear()
        .domain(d3.extent(emotionData, d => d.sentence_index))
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(emotionData, d => {
            let sum = 0;
            emotionTypes.forEach(emotion => sum += d[emotion]);
            return sum;
        })])
        .range([height, 0]);

    // Create color scale
    const color = d3.scaleOrdinal()
        .domain(emotionTypes)
        .range(d3.schemeCategory10);

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(10));

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add area layers
    svg.selectAll(".layer")
        .data(stackedData)
        .enter()
        .append("path")
        .attr("class", "layer")
        .style("fill", d => color(d.key))
        .attr("d", d3.area()
            .x(d => x(d.data.sentence_index))
            .y0(d => y(d[0]))
            .y1(d => y(d[1]))
        );
}

// Function to redo the analysis
function redoAnalysis() {
    document.getElementById('sentenceInput').value = '';
    d3.selectAll("svg").remove();
    document.getElementById('summaryText').textContent = '';
    document.getElementById('uploadMessage').classList.add('hidden'); // Ensure the upload message is hidden
}

// Function to visualize Named Entities
function visualizeEntities(data) {
    const sentences = data.sentences;

    // Remove existing content
    const entitiesContainer = document.getElementById('entities');
    entitiesContainer.innerHTML = '';

    sentences.forEach((sentenceEntry, index) => {
        const sentenceDiv = document.createElement('div');
        sentenceDiv.classList.add('sentence-entry');

        const sentenceText = document.createElement('p');
        sentenceText.innerHTML = `<strong>Sentence ${index + 1}:</strong> ${sentenceEntry.sentence}`;
        sentenceDiv.appendChild(sentenceText);

        // Display entities
        if (sentenceEntry.entities && sentenceEntry.entities.length > 0) {
            const entitiesList = document.createElement('ul');
            sentenceEntry.entities.forEach(entity => {
                const entityItem = document.createElement('li');
                entityItem.innerHTML = `<strong>${entity.text}</strong> (${entity.label})`;
                entitiesList.appendChild(entityItem);
            });
            sentenceDiv.appendChild(entitiesList);
        } else {
            const noEntities = document.createElement('p');
            noEntities.innerText = 'No entities found.';
            sentenceDiv.appendChild(noEntities);
        }

        entitiesContainer.appendChild(sentenceDiv);
    });
}

// Function to visualize emotion intensity as a temperature scale
function visualizeEmotionIntensity(requestId) {
    fetch(`/emotion_intensity/${requestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            // Prepare data
            const emotions = Object.keys(data);
            const intensities = Object.values(data);

            // Map data into an array of objects
            const emotionData = emotions.map((emotion, index) => ({
                emotion: emotion,
                intensity: intensities[index]
            }));

            // Visualize using D3.js
            renderTemperatureScale(emotionData);
        })
        .catch(error => console.error('Error fetching emotion intensity:', error));
}

// Function to render the temperature scale visualization
function renderTemperatureScale(emotionData) {
    // Remove any existing visualization
    d3.select("#emotionIntensityScale").selectAll("*").remove();

    // Set dimensions
    const width = 600;
    const barHeight = 30;
    const height = barHeight * emotionData.length;

    const svg = d3.select("#emotionIntensityScale")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // Define scales
    const xScale = d3.scaleLinear()
        .domain([0, 1])  // Intensity values are between 0 and 1
        .range([0, width - 150]);  // Leave space for labels

    // Define color scale (from cool to warm colors)
    const colorScale = d3.scaleLinear()
        .domain([0, 1])
        .range(["#ADD8E6", "#FF4500"]);  // Light blue to orange-red

    // Create bars
    const bars = svg.selectAll("g")
        .data(emotionData)
        .enter()
        .append("g")
        .attr("transform", (d, i) => `translate(150, ${i * barHeight})`);  // Leave space for labels

    bars.append("rect")
        .attr("width", d => xScale(d.intensity))
        .attr("height", barHeight - 5)
        .attr("fill", d => colorScale(d.intensity));

    // Add emotion labels
    bars.append("text")
        .attr("x", -10)
        .attr("y", barHeight / 2)
        .attr("dy", ".35em")
        .attr("text-anchor", "end")
        .text(d => d.emotion);

    // Add intensity labels at the end of bars
    bars.append("text")
        .attr("x", d => xScale(d.intensity) + 5)
        .attr("y", barHeight / 2)
        .attr("dy", ".35em")
        .attr("text-anchor", "start")
        .text(d => (d.intensity * 100).toFixed(1) + "%");
}

