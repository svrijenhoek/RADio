library(ggplot2)
library(data.table)
library(dplyr)

d <- read.csv("data/output.csv") %>%
  setDT %>%
  .[, impr_index:=NULL] %>%
  melt(id.vars = c("X", "rec_type"), variable.name ="metric")

ggplot(d, aes(x = value, y = rec_type, color = rec_type)) +
  geom_violin(draw_quantiles = c(0.25, 0.5, 0.75)) +
  facet_wrap(~metric, nrow=1, scales = "free_x") +
  theme_classic()



ggplot(d, aes(x = value, y = rec_type)) +
  geom_boxplot() +
  facet_wrap(~metric, nrow=1)
