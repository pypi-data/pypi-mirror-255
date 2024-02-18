movie=pd.read_csv('Z:/ml-latest-small/movies.csv')
ratings=pd.read_csv('Z:/ml-latest-small/ratings.csv')
rating_matrix=ratings.pivot_table(index='userId',columns='movieId',values='rating')
movie_corr=rating_matrix.corr(method='pearson',min_periods=50)
def recommendation(movie_title,top_n):
    similar_score=movie_corr[movie_title]*(rating_matrix.count()-1)
    similar_score=similar_score.sort_values(ascending=False)
    similar_movies=similar_score.head(top_n).index.tolist()
    return similar_movies
movieId=1
result=recommendation(movieId,5)
moviename=movie.loc[movieId,"title"]
print("Top Recommendations for Movies:")
for i in range(0,5):
    print(movie.loc[result[i],"title"])