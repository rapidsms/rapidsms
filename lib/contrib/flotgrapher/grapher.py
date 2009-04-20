'''Generates a javascript string to display flot graphs.
Please read README_flot_grapher.txt

Eliane Stampfer: eliane.stampfer@gmail.com
April 2009'''

class FlotGraph(object):
	
	#constructor.  Accepts an array of data, a title, an array of toggle-able data, and the 
	#width and height of the graph.  All of these values are set to defaults if they are not provided.
	def __init__(self, data=[], title='', toggle_data=[], width='600', height='300'):
		self.display_title = title
		self.title = title.replace(" ", "_")
		self.data = data
		self.height = height
		self.width = width
		self.xaxis_options=''
		self.toggle_data = toggle_data
		self.markings = []
		self.enable_zoom = 1
		self.zoomable = self.enable_zoom
		self.enable_tooltip = 1
		self.show_tooltip = self.enable_tooltip
		self.xaxis_mode = "null"
		self.yaxis_mode = "null"
		self.xaxis_min = "null"
		self.xaxis_max = "null"
		self.yaxis_min = "null"
		self.yaxis_max = "null"
		self.time_format = "%d/%m/%y"
		self.key_outside = 1
		self.key_position = self.key_outside
		self.javascript_string = ""
	#/constructor

#Getters and Setters

	#1 sets the key to outside the graph, anything else sets it to inside the graph.
	def set_key_position(self, key_position):
		self.key_position = key_position

	def get_key_position(self):
		return self.key_position

	#1 enables zoom, anything else disables it
	def set_zoomable(self, zoomable):
		 self.zoomable = zoomable

	def get_zoomable(self):
		 return self.zoomable

	#1 enables showing the tooltip, anything else disables it
	def set_show_tooltip(self, tooltip):
		 self.show_tooltip = tooltip

	def get_show_tooltip(self):
		 return self.show_tooltip

	def set_markings(self, markings_array):
		self.markings = markings_array

	def get_markings(self):
		return self.markings

	def set_display_title(self, display_title):
		 self.display_title = display_title

	def get_display_title(self):
		 return self.display_title	

	def set_title(self, title):
		 self.title = title.replace(" ", "_")

	def get_title(self):
		 return self.title

	def set_data(self, data):
		 self.data = data

	def get_data(self):
		 return self.data

	def set_toggle_data(self, toggle_data):
		 self.toggle_data = toggle_data

	def get_toggle_data(self):
		 return self.toggle_data

	def set_height(self, height):
		 self.height = height

	def get_height(self):
		 return self.height

	def set_width(self, width):
		 self.width = width

	def get_width(self):
		 return self.width

	def set_xaxis_min(self, xaxis_min):
		 self.xaxis_min = xaxis_min

	def get_xaxis_min(self):
		 return self.xaxis_min

	def set_xaxis_max(self, xaxis_max):
		 self.xaxis_max = xaxis_max

	def get_xaxis_max(self):
		 return self.xaxis_max

	def set_yaxis_min(self, yaxis_min):
		 self.yaxis_min = yaxis_min

	def get_yaxis_min(self):
		 return self.yaxis_min

	def set_yaxis_max(self, yaxis_max):
		 self.yaxis_max = yaxis_max

	def get_yaxis_max(self):
		 return self.yaxis_max

	def set_xaxis_mode(self, xaxis_mode):
		 if xaxis_mode == "time": 
				self.xaxis_mode = "\"" + xaxis_mode + "\"" 
		 if xaxis_mode == "null":
				self.xaxis_mode = "null"

	def get_xaxis_mode(self):
		 return self.xaxis_mode

	def set_yaxis_mode(self, yaxis_mode):
		 if yaxis_mode == "time": 
				self.yaxis_mode = "\"" + yaxis_mode + "\"" 
		 if yaxis_mode == "null":
				self.yaxis_mode = "null"

	def get_yaxis_mode(self):
		 return self.yaxis_mode

	def set_time_format(self, time_format):
		 self.time_format = time_format

	def get_time_format(self):
		 return self.time_format

	def get_plot_div(self):
		return "plot_" + self.get_title()	
#/getters and setters	
				

#Methods that create the javascript string

	#called by generate_javascript()
	def get_heading_string(self):
		string = "<h1>"+self.display_title+"</h1> \n"
		string += "<div style=\"float:left\"> \n"
		string += "\t<div id=\""+self.get_plot_div()+"\"></div>\n\t<p id=\""+self.get_title()+"_choices\">\n"
		string += "<p id=\"message\"></p>"
		string += "\t</p>\n"
		if(self.get_zoomable() == self.enable_zoom):
			string += "\t<p> <span id=\""+self.get_title()+"_xselection\"></span></p>\n"
			string += "\t<p> <span id=\""+self.get_title()+"_yselection\"></span></p>\n"
		string += "</div> \n"
		string += "<div id=\""+self.get_plot_div()+"_miniature\" style=\"float:left;margin-left:20px;margin-top:50px\"> \n"
		string += "\t<div id=\""+self.get_plot_div()+"_overview\" style=\"width:166px;height:100px\"></div> \n"
		string += "\t<p id=\""+self.get_plot_div()+"_overviewLegend\" style=\"margin-left:10px\"></p>\n </div> \n\
		<script id=\"source\" language=\"javascript\" type=\"text/javascript\">\n\
		$(function(){\n"
		return string;

	#called by get_options_string()
	def get_markings_string(self):
		string = "\t\t\t\t\tmarkings: [\n"
		for mark_area in self.markings:
			string += "\t\t\t\t\t\t{"
			if('xaxis' in mark_area):
				xaxis = mark_area['xaxis']
				if('from' in xaxis and 'to' in xaxis):
					string += "xaxis: {from: "+xaxis['from']+", to: "+xaxis['to']+"}, "
			if('yaxis' in mark_area):
				yaxis = mark_area['yaxis']
				if('from' in yaxis and 'to' in yaxis):
					string += "yaxis: {from: "+yaxis['from']+", to: "+yaxis['to']+"}, "
			if('color' in mark_area):
				string += "color: \""+ mark_area['color']+"\""
				if('label' in mark_area):
					series_data = self.get_data()
					series_data.append({'data': [], 'label': mark_area['label'], 'color': mark_area['color']})
					self.set_data(series_data)
			string += "},\n"
		string += "\t\t\t\t\t],\n"
		return string
 
	#called by generate_javascript()
	def get_options_string(self):
		string = "\n\
		var options = {\n\
				legend: {\n"
		if (self.get_zoomable() == self.enable_zoom):
			string += "\t\t\t\t\tshow: false,\n"
		string += "\t\t\t\t\tmargin: 5,\n\
					backgroundOpacity:.05,\n"
		if (not(self.get_zoomable() == self.enable_zoom)):
			if (self.get_key_position() == self.key_outside):
				string += "\t\t\t\t\tcontainer: $(\"#"+self.get_plot_div()+"_overviewLegend\")\n"
		string +="\t\t\t\t},\n\
				grid: { \n\
					clickable: true,\n\
					hoverable: true,\n"
		
		string += self.get_markings_string()
		string += "\t\t\t\t},\n\
				selection: { \n\
					mode: \"xy\"\n\
				},\n"
				
				
		string += self.get_axis_options()
		string += "\n\
		};\n"
		return string
	
	#called by get_options_string()
	def get_axis_options(self):
		string = "\n\
				xaxis: {\n\
					mode: "+ self.get_xaxis_mode()+",\n\
					timeformat: \""+ self.time_format +"\",\n\
					min: "+self.get_xaxis_min()+",\n\
					max: "+self.get_xaxis_max()+", \n\
				},"
		string += "\n\
				yaxis: {\n\
					mode: "+ self.get_yaxis_mode()+",\n\
					timeformat: \""+ self.time_format +"\",\n\
					min: "+self.get_yaxis_min()+",\n\
					max: "+self.get_yaxis_max()+", \n\
				},"
		return string

	#called by generate_javascript()
	def get_toggle_datasets_string(self):
		string = "\n\nvar datasets = {"
		counter = 0
		string += self.get_series_string(self.toggle_data, 1)
		#hard-code color indices to prevent them from shifting as
      #series are turned on/off
		string += "}\n"
		string += "var i = "+ str(len(self.data)) + ";\n\
      $.each(datasets, function(key, val) {\n\
        val.color = i;\n\
        ++i;\n\
      });\n"
		return string

	#called by generate_javascript()
	def get_choice_container_string(self):
		return "var choiceContainer = $(\"#"+self.get_title()+"_choices\");\n\
    		$.each(datasets, function(key, val) {\n\
        	choiceContainer.append('<br/><input type=\"checkbox\" name=\"' + key +\n\
                               '\" checked=\"checked\" >' + val.label + '</input>');\n\
    		});\n\
    		choiceContainer.find(\"input\").click(plotGraph);\n"

	#called by generate_javascript()
	def get_plot_area_string(self):
		string =  "\n\
			var plotarea = $(\"#" + self.get_plot_div() + "\");\n\
     			plotarea.css(\"height\", \"" + str(self.get_height()) + "px\");\n\
      		plotarea.css(\"width\", \"" + str(self.get_width())+ "px\");\n\n"
		return string

	#called by get_plot_choices_string() and get_toggle_datasets_string()
	def get_series_string(self, data_array, toggle=0):
		counter = 1
		string = ""
		for series in data_array:
			if('label' in series):
				name = series['label']
			else:
				name = "series "+str(counter)
				counter += 1
			if(toggle == 1):
				name_internal = name.lower()
				string += " \n \t\t\t\"" + name_internal.replace(" ", "_") + "\":"
			string += "{\n\
				label: \"" + name + "\",\n"
			if('lines' in series):
				lines_dict = series['lines']
				string += "\t\t\t\tlines: {\n\t\t\t\t\tshow: true, \n"
				if('lineWidth' in lines_dict and lines_dict['lineWidth'].isdigit()):
					string += "\t\t\t\t\tlineWidth: "+ str(lines_dict['lineWidth']) +",\n"
				if('fill' in lines_dict): 
					string += "\t\t\t\t\tfill: "+str(lines_dict['fill']) +",\n"
				string += "\t\t\t\t},\n"
			if('bars' in series):
				bars_dict = series['bars']
				string += "\t\t\t\tbars: {\n\t\t\t\t\tshow: true, \n"
				if('barWidth' in bars_dict): 
					string += "\t\t\t\t\tbarWidth: "+str(bars_dict['barWidth']) +",\n"
				if('align' in bars_dict and (bars_dict['align'] == "left" or bars_dict['align'] == "center")):
					string += "\t\t\t\t\talign: \""+str(bars_dict['align']) +"\",\n"
				if('fill' in bars_dict): 
					string += "\t\t\t\t\tfill: "+str(bars_dict['fill']) +",\n"
				string += "\t\t\t\t},\n"
			if('points' in series):
				points_dict = series['points']
				string += "\t\t\t\tpoints: {\n\t\t\t\t\tshow: true, \n"
				if('radius' in points_dict and points_dict['radius'].isdigit()):
					string += "\t\t\t\t\tradius: "+ str(points_dict['radius']) +",\n"
				string += "\t\t\t\t},\n"
			if(not('lines' in series) and not('bars' in series) and not ('points' in series)):
				string += "\t\t\t\tlines: {\n\t\t\t\t\tshow: true\n\t\t\t\t}, \n\t\t\t\tpoints: {\n\t\t\t\t\tshow: true\n\t\t\t\t},\n"
			if('color' in series):
				string += "\t\t\t\tcolor: \""+series['color']+"\",\n"
			string += "\t\t\t\tdata: [\n\t\t\t\t\t"
			for point in series['data']:
				string += "[" + str(point[0]) +", " + str(point[1]) + "],"
			string += "\n\t\t\t\t]\n\t\t\t},"
		return string
		#/get_series_string

	#called by generate_javascript()
	def get_plot_choices_string(self):
		string = "function getChoices() {\n\
			\n\
			var data = ["
		string += self.get_series_string(self.data)
		string += "];\n\
        choiceContainer.find(\"input:checked\").each(function () {\n\
            var key = $(this).attr(\"name\");\n\
            if (key && datasets[key])\n\
                data.push(datasets[key]);\n\
        });\n\
			\n\
        return data;\n\
    }\n"
		return string
	
	#called by generate_javascript() if the tooltip is enabled.
	def get_show_tooltip_string(self):
		string = "function showTooltip(x, y, contents) {\n\
        $('<div id=\""+self.get_title()+"_tooltip\">' + contents + '</div>').css( {\n\
            position: 'absolute',\n\
            display: 'none',\n\
            top: y + 5,\n\
            left: x + 5,\n\
            border: '1px solid #fdd',\n\
            padding: '2px',\n\
            'background-color': '#fee',\n\
            opacity: 0.80\n\
        }).appendTo(\"body\").fadeIn(200);\n\
    }\n"
		string += "var previousPoint = null;\n\
    $(\"#" + self.get_plot_div() + "\").bind(\"plothover\", function (event, pos, item) {\n\
        $(\"#x\").text(pos.x.toFixed(2));\n\
        $(\"#y\").text(pos.y.toFixed(2));\n"
		string += "if (item) {\n\
                if (previousPoint != item.datapoint) {\n\
                    previousPoint = item.datapoint;\n"
		string += "\n $(\"#"+self.get_title()+"_tooltip\").remove();\n\
                    var x = item.datapoint[0].toFixed(2),\n\
                        y = item.datapoint[1].toFixed(2);\n\n\
                    showTooltip(item.pageX, item.pageY, item.series.label + \": (\" + x + \", \" + y+ \")\");\n\
                }\n\
            }\n\
            else {\n\
                $(\"#"+self.get_title()+"_tooltip\").remove();\n"
		string += "previousPoint = null;\n }\n });"
		return string
		
	#called by generate_javascript()
	def get_plot_graph_string(self):
		string = "var first = 0;\n\
function plotGraph(min_x, max_x, min_y, max_y){\n\
	data = getChoices();\n\
	if (min_x != null && max_x != null && min_y != null && max_y != null){\n\
		$(\"#"+self.get_title()+"_selection\").text(\" \");\n\
		graph_obj = $.plot(plotarea, data,\n\
		$.extend(true, {}, options, {\n\
		xaxis: { min: min_x, max: max_x},\n\
		yaxis:  { min: min_y, max: max_y},\n\
		}));\n\
     	\n\
	}\n\
	else\n\
		var flot_plot = $.plot(plotarea, data, options);\n\
}\n\
plotGraph();\n\
plotOver();\n"
		return string

	#called by generate_javascript()
	def get_zoom_with_overview(self):
		string = "function plotOver(){\nvar data_over = getChoices();\n\
		overview = $.plot($(\"#"+self.get_plot_div()+"_overview\"), data_over, {\n\
        legend: { show: true, container: $(\"#"+self.get_plot_div()+"_overviewLegend\"), },\n\
        shadowSize: 0,\n\
        xaxis: { ticks: 4, min: "+self.get_xaxis_min()+", max: "+self.get_xaxis_max()+",},\n\
        yaxis: { ticks: 3, min: "+self.get_yaxis_min()+", max: "+self.get_yaxis_max()+",},\n\
		  grid: {clickable: true, autoHighlight: false, " +self.get_markings_string()+"},\n\
        selection: { mode: \"xy\" }\n\
    });\n}\n"
		string += " $(\"#"+self.get_plot_div()+"\").bind(\"plotselected\", function (event, ranges){ \n"
		string += "\n\
        // clamp the zooming to prevent eternal zoom \n\
        if (ranges.xaxis.to - ranges.xaxis.from < 0.00001)\n\
            ranges.xaxis.to = ranges.xaxis.from + 0.00001;\n\
        if (ranges.yaxis.to - ranges.yaxis.from < 0.00001)\n\
            ranges.yaxis.to = ranges.yaxis.from + 0.00001;\n\
        \n\
        // do the zooming\n\
		  plotGraph(ranges.xaxis.from, ranges.xaxis.to, ranges.yaxis.from, ranges.yaxis.to);\n\
		  $(\"#"+self.get_title()+"_xselection\").text(\"x-axis: \" +ranges.xaxis.from.toFixed(1) + \" to \" +ranges.xaxis.to.toFixed(1))\n"
		string += "$(\"#"+self.get_title()+"_yselection\").text(\"y-axis: \" +ranges.yaxis.from.toFixed(1) + \" to \" +ranges.yaxis.to.toFixed(1))\n\
        // don't fire event on the overview to prevent eternal loop\n\
        overview.setSelection(ranges, true);\n\
    });\n"
		string += "$(\"#"+self.get_plot_div()+"_overview\").bind(\"plotselected\", function (event, ranges) {\n\
        plot.setSelection(ranges);\n\
    });\n"
		string += "$(\"#"+self.get_plot_div()+"_overview\").bind(\"plotclick\", function (event, pos) {\n\
			var axes = overview.getAxes();\n\
			var y_min = axes.yaxis.min;\n\
			var y_max = axes.yaxis.max;\n\
			var x_min = axes.xaxis.min;\n\
			var x_max = axes.xaxis.max;\n\
		 plotGraph(x_min, x_max, y_min, y_max);\n\
        });\n"
		return string 

	#called by generate_javascript()
	def get_footer_string(self):
		return " });\n\
		</script>"
		
	#assembles the javascript string
	def generate_javascript(self):
		javascript_string = self.get_heading_string()
		javascript_string += self.get_options_string()
		javascript_string += self.get_toggle_datasets_string()
		javascript_string += self.get_choice_container_string()
		javascript_string += self.get_plot_area_string()
		javascript_string += self.get_plot_choices_string()
		if(self.get_show_tooltip() == self.enable_tooltip):
			javascript_string += self.get_show_tooltip_string()
		javascript_string += self.get_plot_graph_string()
		if(self.get_zoomable() == self.enable_zoom):
			javascript_string += self.get_zoom_with_overview()
		javascript_string += self.get_footer_string()     
		javascript_string.replace("\\n", "\n")
		javascript_string.replace("\\t", "\t")
		self.javascript_string = javascript_string
		return javascript_string

		
	

