from IPython.core.display import HTML
import threading
from IPython.display import display, Image
import ipywidgets as widgets
import time
import queue
import subprocess
import datetime
import matplotlib
import matplotlib.pyplot as plt
from IPython.display import set_matplotlib_formats
import os 
import warnings
from .disclaimer import *
#Global variable PROG_START
PROG_START = 0

def videoHTML(title, videos_list, stats=None):
    '''
       title: string, h2 size
       video: source to videos to display in form of list []
       stats: path to txt file to display any metrics for the output
    '''
    if stats:
        with open(stats) as f:
            time = f.readline()
            frames = f.readline()
        stats_line = "<p>{frames} frames processed in {time} seconds</p>".format(frames=frames, time=time)

    else:
        stats_line = ""
    video_string = ""
    height = '480' if len(videos_list) == 1 else '240'
    for x in range(len(videos_list)):
        video_string += "<video alt=\"\" controls autoplay muted height=\""+height+"\"><source src=\""+videos_list[x]+"\" type=\"video/mp4\" /></video>"
    return HTML('''<h2>{title}</h2>
    {stats_line}
    {videos}
    '''.format(title=title, videos=video_string, stats_line=stats_line))



def outputHTML(title, result_path, output_type, stats=None):
		'''
		device: tuple of edge and accelerator
		'''
		op_list = []
		stats = result_path+'/stats.txt'
		for vid in os.listdir(result_path):
			if vid.endswith(output_type):
				op_list.append(result_path+'/'+vid)
		if os.path.isfile(stats):
			with open(stats) as f:
				time = f.readline()
				frames = f.readline()
				text = f.readline()
			if text:
				stats_line = text
			else:
				stats_line = "<p>{frames} frames processed in {time} seconds</p>".format(frames=frames, time=time)
		else:
			stats_line = ""
		op_string = ""
		height = '480' if len(op_list) == 1 else '120'
		if output_type == ".mp4":
			for x in range(len(op_list)):
				op_string += "<video alt=\"\" controls autoplay muted height=\""+height+"\"><source src=\""+op_list[x]+"\" type=\"video/mp4\" /></video>"
		elif output_type == ".png":
			for x in range(len(op_list)):
				op_string += "<img src='{img}' width='783' height='{height}'>".format(img=op_list[x], height=height)
		return HTML('''<h2>{title}</h2>
    				{stats_line}
    				{op}
    				'''.format(title=title, op=op_string, stats_line=stats_line))




def summaryPlot(results_list, x_axis, y_axis, title, plot, colors=None, disclaimer=None):
    ''' Bar plot input:
	results_dict: dictionary of path to result file and label {path_to_result:label}
	x_axis: label of the x axis
	y_axis: label of the y axis
	title: title of the graph
    '''
    warnings.filterwarnings('ignore')
    if plot=='time':
        clr = 'xkcd:blue'
    else:
        clr = 'xkcd:azure'
    if colors is not None:
        clr = colors
    # If the disclaimer is not specified, it defaults to None
    # and then replaced with the default text below:
    if disclaimer is None:
        disclaimer=defaultDisclaimer()

    plt.figure(figsize=(15, 8))
    plt.title(title , fontsize=28, color='black', fontweight='bold')
    plt.ylabel(y_axis, fontsize=16, color=clr)
    plt.xlabel(x_axis, fontsize=16, color=clr)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    val = []
    arch = []
    diff = 0
    for path, hw in results_list:
        #Check if the stat file exist and not empty
        if os.path.isfile(path) and os.path.getsize(path) != 0:
            f = open(path, "r")
            l1_time = float(f.readline())
            l2_count = float(f.readline())
            if plot=="time":
                val.append(l1_time)
            elif plot=="fps":
                val.append((l2_count/l1_time))
            f.close()
        else:
            val.append(0)
        arch.append(hw)

    offset = max(val)/100
    for v in val:
        if v == 0:
            data = 'N/A'
            y = 0
        else:
            precision = 2 
            if v >= pow(10, precision):
                data = '{:.0f}'.format(round(v/pow(10, precision+1), precision)*pow(10, precision+1))
            else:
                data = '{{:.{:d}g}}'.format(round(precision)).format(v)
            y = v + offset   
        plt.text(diff, y, data, fontsize=14, multialignment="center",horizontalalignment="center", verticalalignment="bottom",  color='black')
        diff += 1
    plt.ylim(top=(max(val)+10*offset))
    plt.bar(arch, val, width=0.8, align='center', color=clr)
    plt.pause(1)
    # to disable the disclaimer display, supply "disclaimer=False" argument
    if disclaimer:
        display(widgets.HTML(value=disclaimer))



def summaryPlotWithURL(results_list, x_axis, y_axis, title, plot, colors=None, disclaimer=None):
    ''' Bar plot input:
	results_dict: dictionary of path to result file and label {path_to_result:label}
	x_axis: label of the x axis
	y_axis: label of the y axis
	title: title of the graph
        plot: plot type (time, fps)
    '''
    warnings.filterwarnings('ignore')
    set_matplotlib_formats("svg")
    if plot=='time':
        clr = 'xkcd:blue'
    else:
        clr = 'xkcd:azure'
    if colors is not None:
        clr = colors
    # If the disclaimer is not specified, it defaults to None
    # and then replaced with the default text below:
    if disclaimer is None:
        disclaimer=defaultDisclaimer()

    plt.figure(figsize=(11, 7))
    plt.title(title , fontsize=24, color='black', fontweight='bold')
    plt.ylabel(y_axis, fontsize=12, color=clr)
    plt.xlabel(x_axis, fontsize=12, color=clr,  labelpad=60, verticalalignment='top')
    #plt.xticks(fontsize=16)
    plt.xticks([])
    plt.yticks(fontsize=12)

    val = []
    arch = []
    xlab = []
    URLs = []
    xv = 0
    diff = 0
        
    for path, hw, url in results_list:
        #Check if the stat file exist and not empty
        if os.path.isfile(path) and os.path.getsize(path) != 0:
            f = open(path, "r")
            l1_time = float(f.readline())
            l2_count = float(f.readline())
            if plot=="time":
                val.append(l1_time)
            elif plot=="fps":
                val.append((l2_count/l1_time))
            f.close()
        else:
            val.append(0)
        arch.append(hw)
        URLs.append(url)
        xlab.append(xv)
        xv += 1

    offset = max(val)/100
    
    for v in val:
        if v == 0:
            data = 'N/A'
            y = 0
        else:
            precision = 2 
            if v >= pow(10, precision):
                data = '{:.0f}'.format(round(v/pow(10, precision+1), precision)*pow(10, precision+1))
            else:
                data = '{{:.{:d}g}}'.format(round(precision)).format(v)
            y = v + offset   
        plt.text(diff, y, data, fontsize=12, multialignment="center",horizontalalignment="center", verticalalignment="bottom",  color='black')
        diff += 1
    plt.ylim(top=(max(val)+10*offset))
    
    plt.bar(xlab, val, width=0.8, align='center', color=clr)
    d = -0.35
    for name, link in zip(arch, URLs):
        plt.annotate(name, xy=(2,2), xytext=(d, -3.0),url=link, color='tab:blue', fontsize=12, verticalalignment='top', bbox=dict(color='w', alpha=1e-6, url=link))
        d += 1
    plt.pause(1)
    # to disable the disclaimer display, supply "disclaimer=False" argument
    if disclaimer:
        display(widgets.HTML(value=disclaimer))



def liveQstat():
    cmd = ['qstat']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output,_ = p.communicate()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    qstat = widgets.Output(layout={'width': '100%', 'height': '300px', 'border': '1px solid gray'})
    stop_signal_q = queue.Queue()

    def _work(qstat,stop_signal_q):
        while stop_signal_q.empty():
            cmd = ['qstat']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output,_ = p.communicate()
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            qstat.append_stdout(now+'\n\n'+output.decode()+'\n\n\n')
            time.sleep(10.0)
            qstat.clear_output(wait=False)
        print('liveQstat stopped')
    thread = threading.Thread(target=_work, args=(qstat, stop_signal_q))

    thread.start()
    sb = widgets.Button(description='Stop')
    def _stop_qstat(evt):
        stop_signal_q.put(True)
    sb.on_click(_stop_qstat)
    display(qstat)
    display(sb)

   
def progressIndicator(path, file_name , title, min_, max_):
    '''
	Progress indicator reads first line in the file "path" 
	path: path to the progress file
        file_name: file with data to track
	title: description of the bar
	min_: min_ value for the progress bar
	max_: max value in the progress bar

    '''
    style = {'description_width': 'initial'}
    progress_bar = widgets.FloatProgress(
    value=0.0,
    min=min_,
    max=max_,
    description=title,
    bar_style='info',
    orientation='horizontal',
    style=style
)
    remain_time = widgets.HTML(
    value='0',
    placeholder='0',
    description='Remaining:',
    style=style
)
    est_time = widgets.HTML(
    value='0',
    placeholder='0',
    description='Total Estimated:',
    style=style
)

    progress_bar.value=min_

    #Check if results directory exists, if not create it and create the progress data file
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    f = open(path+'/'+file_name, "w")
    f.close()
    
    def _work(progress_bar, est_time,remain_time,  path):
        box_layout = widgets.Layout(display='flex', flex_flow='column', align_items='stretch', border='ridge', width='70%', height='')
        box = widgets.HBox([progress_bar, est_time, remain_time], layout=box_layout)
        display(box)
        # progress
        last_status = 0.0
        remain_val = '0'
        est_val = '0'
        output_file = path
        while last_status < 100:
            if os.path.isfile(output_file):
                with open(output_file, "r") as fh:
                    line1 = fh.readline() 	#Progress 
                    line2 = fh.readline()  	#Remaining time
                    line3 = fh.readline()  	#Estimated total time
                    if line1 and line2 and line3:
                        last_status = float(line1)
                        remain_val = line2
                        est_val = line3
                    progress_bar.value = last_status
                    remain_time.value = remain_val+' seconds' 
                    est_time.value = est_val+' seconds' 
            else:
                cmd = ['ls']
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                output,_ = p.communicate()
        remain_time.value = '0'+' seconds' 
        time.sleep(1)
        os.remove(output_file)


    thread = threading.Thread(target=_work, args=(progress_bar, est_time, remain_time, os.path.join(path, file_name)))
    thread.start()
    time.sleep(0.1)


def simpleProgressUpdate(file_name, current_time, estimated_time):
    progress = round(100*current_time/estimated_time, 1)
    remaining_time = round(estimated_time-current_time, 1)
    estimated_time = round(estimated_time, 1)
    with  open(file_name, "w") as progress_file:
        progress_file.write(str(progress)+'\n')
        progress_file.write(str(remaining_time)+'\n')
        progress_file.write(str(estimated_time)+'\n')


class ProgressUpdate:

    def __init__(self):
        self.progress_data = []
        self.latest_update = []
        self.main_thread = threading.current_thread()
        def _writeToFile(progress, latest_update):
            more_data = True
            while more_data:
                for  id_, (new_data, latest) in enumerate(zip(self.progress_data, self.latest_update)):
                    if not self.main_thread.is_alive():
                        more_data = False
                    file_name, time_diff, frame_count, video_len = new_data
                    file_name, last_c = latest
                    if last_c == frame_count:
                        continue
                    else:
                        self.latest_update[id_] = [file_name, frame_count]
                        progress = round(100*(frame_count/video_len), 1)
                        remaining_time = round((time_diff/frame_count)*(video_len-frame_count), 1)
                        estimated_time = round((time_diff/frame_count)*video_len, 1)
                        with  open(file_name, "w+") as progress_file:
                            progress_file.write(str(progress)+'\n')
                            progress_file.write(str(remaining_time)+'\n')
                            progress_file.write(str(estimated_time)+'\n')
                time.sleep(1)
               

        self.thread = threading.Thread(target=_writeToFile, args=(self.progress_data, self.latest_update))
        if not self.thread.is_alive():
            self.thread.start()


    def progress(self, file_name, time_diff, frame_count, video_len):
        for id_, item in enumerate(self.progress_data):
            file_, _, _, _ = item
            if file_name == file_:
                self.progress_data[id_] = [file_name, time_diff, frame_count, video_len]
                return
        self.progress_data.append([file_name, time_diff, frame_count, video_len])
        self.latest_update.append([file_name, -1])
        
 

def progressUpdate(file_name, time_diff, frame_count, video_len):
    global PROG_START
    if not isinstance(PROG_START, ProgressUpdate):
        print("Create progress tracker")
        PROG_START = ProgressUpdate()
    PROG_START.progress(file_name, time_diff, frame_count, video_len)

