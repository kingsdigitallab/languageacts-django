$(document).ready(function()
{   
    $(document).foundation();

    // LAWM Cookie
    if (!Cookies.get('lawm-cookie')) {
        $('#cookie-disclaimer').removeClass('hide');
        }
        // Set cookie
        $('#cookie-disclaimer .closeme').on("click", function() {
            Cookies.set('lawm-cookie', 'lawm-cookie-set', { expires: 30 });
        });

    // Instafeed
    if ($('#instafeed').length) {
        var feed = new Instafeed({
            get: 'user',
            userId: '4755811294',
            accessToken: '4755811294.dd6559f.d035b5c4fe104bf68d57b6c6887dc2ca',
            template: '<div class="medium-6 large-3 columns"><a href="{{link}}" target="_blank" title="Open on Instagram site in a new window"><img src="{{image}}" alt="{{caption}}"></a></div>',

            // clientId: 'dd6559f3262d4ff4b533c15451b54817',
            resolution: 'standard_resolution',
            limit: '4'
        });

        feed.run();
    }

    // Expande / Collapse
    $('.toggler').on('click', function () {
        $(this).next('.content').slideToggle(400).toggleClass('hide show');
        $(this).toggleClass('close open');

        return false;
    });

    // This is for the Historical Frequency chart
    if ($('.hist_freq_chart'.length))
    {
        $('.hist_freq_chart').each(function()
        {
            // Grab chart variables
            var x_label = $(this).attr('data-x-label');
            var y_label = $(this).attr('data-y-label');

            var chart_data = $(this).attr('data-chart-data').replace(/(\r\n|\n|\r)/gm, '')
                .split(',')
                .filter(function(el) {return el.length != 0});

            // Get our data into a dict.
            data = [
                {
                    name: "Historical Frequency",
                    values: []
                }
            ]

            for(var i = 0; i < chart_data.length; i++)
            {
                item = chart_data[i].split(':');
                data[0]['values'].push({ 'date': parseInt(item[0].trim()), 'val' : parseInt(item[1].trim()) });
            }

            var width = 500;
            var height = 300;
            var margin = 50;
            var duration = 250;
            
            var lineOpacity = "0.8";
            var lineStroke = "2px";
            var fillOpacity = '0';
            var lineColor = '#14b1e7'; //'rgb(31, 119, 180)';
            var circleOpacity = '1';
            var circleRadius = 5;
            var circleRadiusHover = 10;
            var circleColor = '#f1853a'; //'rgb(31, 119, 180)';
            
            
            /* Format Data */
            var parseDate = d3.timeParse("%Y");
            data.forEach(function(d) { 
              d.values.forEach(function(d) {
                d.date = parseDate(d.date);
                d.val = +d.val;    
              });
            });
            
            
            /* Scale */
            var xScale = d3.scaleTime()
              .domain(d3.extent(data[0].values, d => d.date))
              .range([0, width-margin]);
            
            var yScale = d3.scaleLinear()
              .domain([0, d3.max(data[0].values, d => d.val)])
              .range([height-margin, 0]);
            
            
            /* Add SVG */
            var svg = d3.select(this).append("svg")
              .attr("width", (width+margin)+"px")
              .attr("height", (height+margin)+"px")
              .attr("viewBox", '0 0 ' + (width+margin) + ' ' + (height+margin))
              .append('g')
              .attr("transform", `translate(${margin}, ${margin})`);
            
            
            /* Add line into SVG */
            var line = d3.line()
              .x(d => xScale(d.date))
              .y(d => yScale(d.val));
            
            let lines = svg.append('g')
              .attr('class', 'lines');
            
            lines.selectAll('.line-group')
              .data(data).enter()
              .append('g')
              .attr('class', 'line-group')  
              .append('path')
              .attr('class', 'line')  
              .attr('d', d => line(d.values))
              .style('stroke', lineColor)
              .style('stroke-width', lineStroke)
              .style('fill-opacity', fillOpacity)
              .style('opacity', lineOpacity);
            
            /* Add circles in the line */
            lines.selectAll("circle-group")
              .data(data).enter()
              .append("g")
              .style("fill", circleColor)
              .selectAll("circle")
              .data(d => d.values).enter()
              .append("g")
              .attr("class", "circle")  
              .on("mouseover", function(d) {
                  d3.select(this)     
                    .append("text")
                    .attr("class", "graph-text")
                    .style("opacity", "0")
                    .text(`${d.val}`)
                    .attr("x", d => xScale(d.date) + 5)
                    .attr("y", d => yScale(d.val) - 10)
                    .transition()
                    .duration(duration)
                    .style("opacity", "1");
                })
              .on("mouseout", function(d) {
                  d3.select(this)
                    .transition()
                    .duration(duration)
                    .selectAll(".graph-text")
                    .transition()
                    .duration(duration)
                    .style("opacity", "0") // Not really needed, just for vis. effect
                    .remove();
                })
              .append("circle")
              .attr("cx", d => xScale(d.date))
              .attr("cy", d => yScale(d.val))
              .attr("r", circleRadius)
              .style('opacity', circleOpacity)
              .on("mouseover", function(d) {
                    d3.select(this)
                      .transition()
                      .duration(duration)
                      .style('cursor', 'pointer')
                      .attr("r", circleRadiusHover);
                  })
                .on("mouseout", function(d) {
                    d3.select(this) 
                      .transition()
                      .duration(duration)
                      .attr("r", circleRadius);  
                  });
            
            
            /* Add Axis into SVG */
            var xAxis = d3.axisBottom(xScale).ticks(5);
            var yAxis = d3.axisLeft(yScale).ticks(10);
            
            svg.append("g")
              .attr("class", "x axis")
              .attr("transform", `translate(0, ${height-margin})`)
              .call(xAxis);
            
            svg.append("g")
              .attr("class", "y axis")
              .call(yAxis);
            
        

            svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin)
            .attr("x",0 - ((height - margin)/ 2))
            .attr("dy", "0.8em")
            .style("text-anchor", "middle")
            .style('font-size', '0.8em')
            .text(y_label);

            svg.append("text")
            .attr("x", (width / 2) - margin)
            .attr("y", height - (margin/2))
            .attr("dy", "0.8em")
            .style("text-anchor", "middle")
            .style('font-size', '0.8em')
            .text(x_label);
        });
    }
});