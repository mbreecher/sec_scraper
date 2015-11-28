fact_counts_1 <- read.csv(file.choose(), header = F, stringsAsFactors = F)
fact_counts_2 <- read.csv(file.choose(),header = F, stringsAsFactors = F)

fact_counts_all <- rbind(fact_counts_1, fact_counts_2)
names(fact_counts_all) <- c("CIK", "Account.Name", "Form", "Filed.Date", "Fact.Count", "Std.Tags", "Ext.Tags")

result <- c()
i = 0
indexed <- ddply(fact_counts_all, .var = c("Account.Name"), .fun = function(x){
  loopq <- x[x$Form %in% "10-Q", ]
  if(dim(loopq)[1] > 0){loopq$index <- paste0(loopq$Form, seq(1,nrow(loopq),1))}
  loopk <- x[x$Form %in% "10-K", ]
  if(dim(loopk)[1] > 0){loopk$index <- paste0(loopk$Form, seq(1,nrow(loopk),1))}
  result <- rbind(result, loopq, loopk)
  result  
})

indexed<- indexed[indexed$index %in% c("10-K1", "10-Q1", "10-Q2", "10-Q3"),]

result <- dcast(CIK + Account.Name ~ index, data = indexed, value.var = "Fact.Count", FUN = sum)

setwd("C:/ipy/sec_scraper")
write.csv(result, file = "fact_counts.csv", row.names = F)
