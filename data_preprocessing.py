import datetime
import dart.Util
import dart.preprocess.downloads
import dart.preprocess.nlp
import dart.preprocess.enrich_articles
import dart.preprocess.identify_stories
import dart.preprocess.recommendations


def main():
    
    config = dart.Util.read_full_config_file()

    # downloads external data sources
    print(str(datetime.datetime.now()) + "\tStep 1 of 5: downloading necessary files")
    dart.preprocess.downloads.execute(config)

    # preprocess data
    print(str(datetime.datetime.now()) + "\tStep 2 of 5: data annotation")
    df = dart.preprocess.nlp.execute()

    # enrich articles
    print(str(datetime.datetime.now()) + "\tStep 3 of 5: enriching entities")
    df = dart.preprocess.enrich_articles.Enricher(config).enrich(df)

    print(str(datetime.datetime.now()) + "\tStep 4 of 5: clustering stories")
    df = dart.preprocess.identify_stories.StoryIdentifier(config).execute(df)

    dart.Util.create_pickle(df, config['articles'])

    print(str(datetime.datetime.now()) + "\tStep 5 of 5: processing recommendations")
    dart.preprocess.recommendations.process()

    print(str(datetime.datetime.now()) + "\tdone")


if __name__ == "__main__":
    main()
