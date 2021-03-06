from comp61542 import app
from database import database
from flask import (render_template, request)
import matplotlib.pyplot as plt
import numpy as np

def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([ (fmt % i).rstrip('0').rstrip('.') for i in item ]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result

@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"averages"}
    args['title'] = "Averaged Data"
    args['description'] = "Average statistics for publications, authors and years!"
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [ database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE ]
    tables.append({
        "id":1,
        "title":"Average Authors per Publication",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_per_publication(i)[1])
                for i in averages ] })
    tables.append({
        "id":2,
        "title":"Average Publications per Author",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_per_author(i)[1])
                for i in averages ] })
    tables.append({
        "id":3,
        "title":"Average Publications in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_in_a_year(i)[1])
                for i in averages ] })
    tables.append({
        "id":4,
        "title":"Average Authors in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_in_a_year(i)[1])
                for i in averages ] })

    args['tables'] = tables
    return render_template("averages.html", args=args)

@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"coauthors"}
    args["title"] = "Co-Authors"
    args['description'] = "List all co-authors of an author, between a given time in a given publication type!"


    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)

@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    return render_template('statistics.html', args=args)

@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":status}

    if (status == "publication_summary"):
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary()
        header, data = args["data"]
        titles = ["Conference Paper","Journal", "Book", "Book Chapter", ]
        plotted_label, plotted_data = db.get_plot_data_for_statistic_details(data)
        colors = ['r','g','b','y']

        value = ""
        if "value" in request.args:
            value = request.args.get("value")
            # generateBarChart(titles[0], plotted_label, [titles[0]], colors, [plotted_data[0]])
            # generateBarChart(titles[1], plotted_label, [titles[1]], colors, [plotted_data[1]])
            # generateBarChart(titles[2], plotted_label, [titles[2]], colors, [plotted_data[2]])
            # generateBarChart(titles[3], plotted_label, [titles[3]], colors, [plotted_data[3]])
            generateBarChart(titles[3], plotted_label, titles, colors, 0.1, True, plotted_data)
            #generateBarChart(legends[1], plotted_label, legends[1], colors, data[1])

    if (status == "publication_author"):
        args["title"] = "Author Publication"
        args["data"] = db.get_publications_by_author()

    if (status == "publication_year"):
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year()
        header, data = args["data"]
        value = ""
        if "value" in request.args:
            value = request.args.get("value")
            list = []
            for i in range(len(data)):
                tuple = data[i][0], data[i][5]
                list.append(tuple)
            list.sort(key=lambda x: x[0])
            N = len( list )
            x = np.arange(1, N+1)
            y = [ num for (s, num) in list ]
            max=0
            for num in y:
                if num > max:
                    max = num
            labels = [ s for (s, num) in list ]
            width = 1/1.1
            bar1 = plt.bar( x, y, width, color="y" )
            plt.axis( [0, N+1, 0, max+1])
            plt.xticks(x + width/2.0, labels )
            figManager = plt.get_current_fig_manager()
            figManager.window.showMaximized()
            plt.show()

    if (status == "author_year"):
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()
        header, data = args["data"]
        plotted_label, plotted_data = db.get_plot_data_for_statistic_details(data)
        legends = header[1:(len(header)-1)]
        colors = ["r", "y", "g", "b"]
        value = ""
        if "value" in request.args:
            value = request.args.get("value")
            generateBarChart('Publications of all authors by year', plotted_label, legends, colors, 0.6, True, plotted_data)

    if (status == "appearance_author"):
        args["title"] = "Appearance"
        args["data"] = db.get_number_of_appearance_by_author()

    return render_template('statistics_details.html', args=args)

def generateBarChart(title, labels, legends, colors, width, has_numbers, data):
    fig, ax = plt.subplots()
    ind = np.arange(len(labels))
    rects = ()
    for i in range(len(legends)):
        rect = ax.bar(ind, data[i], width, color = colors[i])
        rects += (rect[0],)
        if has_numbers:
            for rec in rect:
                height = rec.get_height()
                ax.text(rec.get_x()+rec.get_width()/2., 1.05*height, '%d'%int(height),
                        ha='center', va='bottom')

    # add some
    # ax.set_ylabel('Scores')
    ax.set_title(title)
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(labels)

    ax.legend(rects, legends)
    plt.show()


@app.route("/searchauthors")
def showSearchAuthor():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"searchauthor"}
    args['title'] = "Search Author"
    args['description'] = "Input the author's name you want to search!"
    tables = []
    headers = ["Author Name"]
    #, "Conference Paper", "Journal", "Book", "Book Chapter", "Number of times first Author", "Number of times last Author", "All Publications", "Number of CoAuthors"]

    author_name = ""

    if "author_name" in request.args:
        author_name = request.args.get("author_name")

    header, data = db.search_authors(author_name.strip())
    #dataWithDistance = []
    if data == None:
        lastname = author_name.rsplit(None,1)[0]
        firstname = author_name.rsplit(None,1)[::-1][0]
        header, data = db.search_authors(firstname + " " + lastname)
        if data == None:
            data = ()
            headers = ["No author found"]

    if len(data) == 1:
        return showAuthorStats(data[0][0])

    """for i in range(len(data)):
        dataWithDistance.append([data[i], distanceFirstname[i], distanceLastname[i]])"""
    # dataWithDistance = [data, distanceFirstname, distanceLastname]
    tables.append({
        "id":1,
        "title":"Author Statistics Details",
        "header":headers,
        "rows": data})

    args['tables'] = tables

    return render_template('searchauthors.html', args=args)

@app.route("/authorStats/<author_name>")
def showAuthorStats(author_name):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"searchauthor"}
    args['title'] = "Search Author"
    args['description'] = "Results:"
    args['author_name'] = author_name
    tables = []

    value = ""
    if "value" in request.args:
            value = request.args.get("value")
            db.draw_coauthors(author_name)

    tables.append({
        "id":1,
        "title":"Author general statistics",
        "header":["Author Name", "Number of conference papers", "Number of journals", "Number of books", "Number of book chapters", "Total", "Number of Coauthors"],
        "rows": db.get_all_author_stats(author_name)})
    tables.append({
        "id":2,
        "title":"Author first appearances",
        "header":["Author Name", "Appear first in Conference Paper", "Appear first in Journal", "Appear first in Book", "Appear first in Book Chapter", "Total"],
        "rows": db.get_first_author_stats(author_name)})
    tables.append({
        "id":3,
        "title":"Author last appearances",
        "header":["Author Name", "Appear last in Conference Paper", "Appear last in Journal", "Appear last in Book", "Appear last in Book Chapter", "Total"],
        "rows": db.get_last_author_stats(author_name)})
    tables.append({
        "id":4,
        "title":"Sole author statistics",
        "header":["Author Name", "Sole author in Conference Paper", "Sole author in Journal", "Sole author in Book", "Sole author in Book Chapter", "Total"],
        "rows": db.get_sole_author_stats(author_name)})

    args['tables'] = tables

    return render_template('authorStats.html', args=args)

@app.route("/distance")
def showDistance():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"distances"}
    args['title'] = "Distances"
    args['description'] = "Enter two author names to find their degree of separation.<br />X = No connection or author not found"
    if "author_name1" in request.args and "author_name2" in request.args:
        author_name1 = request.args.get("author_name1")
        author_name2 = request.args.get("author_name2")
        if author_name1 != "" and author_name2 != "":
            args['a1'] = author_name1
            args['a2'] = author_name2
            result = db.get_distance_between_authors(author_name1, author_name2)
            args['result'] = "Distance from %s to %s is: %s" % (author_name1, author_name2, result)
            if result == 'X1':
                lastname = author_name1.rsplit(None,1)[0]
                firstname = author_name1.rsplit(None,1)[::-1][0]
                result = db.get_distance_between_authors(firstname + " " + lastname, author_name2)
                if result == 'X1':
                    args['result'] = "Author 1 not found"
                else:
                    args['result'] = "Distance from %s to %s is: %s" % (args['a1'], args['a2'], result)
                    author_name1 = firstname + " " + lastname
            if result == 'X2':
                lastname = author_name2.rsplit(None,1)[0]
                firstname = author_name2.rsplit(None,1)[::-1][0]
                result = db.get_distance_between_authors(author_name1, firstname + " " + lastname)
                if result == 'X2':
                    args['result'] = "Author 2 not found"
                else:
                    args['result'] = "Distance from %s to %s is: %s" % (args['a1'], args['a2'], result)
            if result == 'X':
                lastname1 = author_name1.rsplit(None,1)[0]
                firstname1 = author_name1.rsplit(None,1)[::-1][0]
                lastname2 = author_name2.rsplit(None,1)[0]
                firstname2 = author_name2.rsplit(None,1)[::-1][0]
                if author_name1 == author_name2 or author_name1 == (firstname2 + " " + lastname2) or (firstname1 + " " + lastname1) == author_name2 or (firstname1 + " " + lastname1) == (firstname2 + " " + lastname2):
                    args['result'] = "Same author"
        else:
            args['a1'] = ""
            args['a2'] = ""
            args['result'] = "Invalid author name"
    return render_template('distance.html', args=args)

@app.route("/about")
def showabout():
     dataset = app.config['DATASET']
     db = app.config['DATABASE']
     args = {"dataset":dataset, "id":"about"}
     args['title'] = "About"
     return render_template('about.html', args=args)

#to test dijkstras, not a feature yet (or ever)
@app.route("/test")
def dijkstra():
    db = app.config['DATABASE']
    print db.get_distance_between_authors("Ceri Stefano", "Fraternali Piero")
    # return render_template(statist)